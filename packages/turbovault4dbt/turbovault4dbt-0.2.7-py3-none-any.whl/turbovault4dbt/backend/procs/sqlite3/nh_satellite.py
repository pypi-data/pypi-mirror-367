from numpy import object_
import os
from turbovault4dbt.backend.procs.sqlite3.utils import has_column, sanitize_output_dir


def get_groupname(cursor,object_id):
    query = f"""SELECT DISTINCT GROUP_NAME from non_historized_satellite where NH_Satellite_Identifier = '{object_id}' ORDER BY Target_Column_Physical_Name LIMIT 1"""
    cursor.execute(query)
    return cursor.fetchone()[0]

def gen_payload(payload_list):
    payload_string = ''
    
    for column in payload_list:
        payload_string = payload_string + f'\t- {column.lower()}\n'
    
    return payload_string

def generate_nh_satellite_list(cursor, source, source_name, source_object):

    query = f"""SELECT DISTINCT NH_Satellite_Identifier,Target_Satellite_Table_Physical_Name,Parent_Primary_Key_Physical_Name,GROUP_CONCAT(Target_Column_Physical_Name),
                Source_Table_Physical_Name,Load_Date_Column
                from 
                (SELECT DISTINCT hs.NH_Satellite_Identifier,hs.Target_Satellite_Table_Physical_Name,hs.Parent_Primary_Key_Physical_Name,hs.Target_Column_Physical_Name,
                src.Source_Table_Physical_Name,src.Load_Date_Column FROM non_historized_satellite hs
                inner join source_data src on src.Source_table_identifier = hs.Source_Table_Identifier
                where 1=1
                and src.Source_System = '{source_name}'
                and src.Source_Object = '{source_object}')
                group by NH_Satellite_Identifier,Target_Satellite_Table_Physical_Name,Parent_Primary_Key_Physical_Name,Source_Table_Physical_Name,Load_Date_Column"""

    cursor.execute(query)
    results = cursor.fetchall()

    return results
        

def generate_nh_satellite(data_structure):
    cursor = data_structure['cursor']
    source = data_structure['source']
    generated_timestamp = data_structure['generated_timestamp']
    rdv_default_schema = data_structure['rdv_default_schema']
    model_path = data_structure['model_path']       
    source_name = data_structure['source_name'] 
    source_object = data_structure['source_object']   
    nh_satellite_list = generate_nh_satellite_list(cursor=cursor, source=source, source_name= source_name, source_object= source_object)


    for nh_satellite in nh_satellite_list:
        nh_satellite_name = nh_satellite[1]
        hashkey_column = nh_satellite[2]
        payload_list = nh_satellite[3].split(',')
        source_model = nh_satellite[4].lower()
        loaddate = nh_satellite[5]

        payload = gen_payload(payload_list)
        group_name = 'RDV/' + get_groupname(cursor, nh_satellite[0])

        # --- Query for output_dir for this NH satellite ---
        if has_column(cursor, "non_historized_satellite", "output_dir"):
            cursor.execute("SELECT output_dir FROM non_historized_satellite WHERE NH_Satellite_Identifier = ? LIMIT 1", (nh_satellite[0],))
            result = cursor.fetchone()
            output_dir = result[0] if result and result[0] else ""
        else:
            output_dir = ""


        # --- Build the full output directory ---
        base_model_path = model_path.replace('@@GroupName', group_name).replace('@@SourceSystem', source_name).replace('@@timestamp', generated_timestamp)
        if output_dir:
            output_dir = sanitize_output_dir(output_dir)
            full_model_path = os.path.join(base_model_path, output_dir)
        else:
            full_model_path = base_model_path

        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "nh_sat.txt"), "r") as f:
                command_tmp = f.read()
        except Exception as e:
            data_structure['print2FeedbackConsole'](message=f"Failed to load template nh_sat.txt: {e}")
            return
        command = command_tmp.replace('@@SourceModel', source_model).replace('@@Hashkey', hashkey_column).replace('@@Payload', payload).replace('@@LoadDate', loaddate).replace('@@Schema', rdv_default_schema)

        filename = os.path.join(full_model_path, f"{nh_satellite_name}.sql")

        # --- Ensure the directory exists ---
        if not os.path.exists(full_model_path):
            os.makedirs(full_model_path)

        with open(filename, 'w') as f:
            f.write(command.expandtabs(2))
            if data_structure['console_outputs']:
                data_structure['print2FeedbackConsole'](message=f"Created Satellite Model {nh_satellite_name}")