import os
from turbovault4dbt.backend.procs.sqlite3.utils import has_column, sanitize_output_dir

def get_groupname(cursor,object_id):
    query = f"""SELECT DISTINCT GROUP_NAME from standard_hub where Hub_Identifier = '{object_id}' ORDER BY Is_Primary_Source LIMIT 1"""
    cursor.execute(query)
    return cursor.fetchone()[0]

def generate_hub_list(cursor, source, source_name, source_object):
    
    query = f"""SELECT Hub_Identifier,Target_Hub_table_physical_name,GROUP_CONCAT(distinct Business_Key_Physical_Name)
                from 
                (SELECT h.Hub_Identifier,h.Target_Hub_table_physical_name,(Business_Key_Physical_Name),h.Group_Name    
                FROM standard_hub h
                inner join source_data src on src.Source_table_identifier = h.Source_Table_Identifier
                where 1=1
                and src.Source_System = '{source_name}'
                and src.Source_Object = '{source_object}'
                and h.Is_Primary_Source = '1'
                ORDER BY h.Target_Column_Sort_Order
                )
                group by Hub_Identifier,Target_Hub_table_physical_name
                """

    cursor.execute(query)
    results = cursor.fetchall()

    return results


def generate_source_models(cursor, hub_id):

    command = ""

    query = f"""SELECT Source_Table_Physical_Name,GROUP_CONCAT(Source_Column_Physical_Name),Hashkey,Static_Part_of_Record_Source_Column
                FROM 
                (SELECT src.Source_Table_Physical_Name,h.Source_Column_Physical_Name, h.Target_Primary_Key_Physical_Name as Hashkey,
                src.Static_Part_of_Record_Source_Column 
                FROM standard_hub h
                inner join source_data src on h.Source_Table_Identifier = src.Source_table_identifier
                where 1=1
                and Hub_Identifier = '{hub_id}'
                ORDER BY h.Target_Column_Sort_Order)
                group by Source_Table_Physical_Name,Hashkey,Static_Part_of_Record_Source_Column
                """

    cursor.execute(query)
    results = cursor.fetchall()

    for source_table_row in results:
        source_table_name = '- name: stg_' + source_table_row[0].lower()
        bk_columns = source_table_row[1].split(',')
        hk_column = source_table_row[2]
        if len(bk_columns) > 1: 
            bk_col_output = ""
            for bk in bk_columns: 
                bk_col_output += f"\n\t\t\t- '{bk}'"
        else:
            bk_col_output = "'" + bk_columns[0] + "'"
        
        command += f"\n\t{source_table_name}\n\t\tbk_columns: {bk_col_output}"

        command += f"\n\t\thk_column: {hk_column}"

        rsrc_static = source_table_row[3]

        if rsrc_static != '':
            command += f"\n\t\trsrc_static: '{rsrc_static}'"

    return command


def generate_hashkey(cursor, hub_id):

    query = f"""SELECT DISTINCT Target_Primary_Key_Physical_Name 
                FROM standard_hub
                WHERE hub_identifier = '{hub_id}'"""

    cursor.execute(query)
    results = cursor.fetchall()

    for hashkey_row in results: #Usually a hub only has one hashkey column, so results should only return one row
        hashkey_name = hashkey_row[0] 

    return hashkey_name
            

def generate_hub(data_structure):
    cursor = data_structure['cursor']
    source = data_structure['source']
    generated_timestamp = data_structure['generated_timestamp']
    rdv_default_schema = data_structure['rdv_default_schema']
    model_path = data_structure['model_path']
    source_name = data_structure['source_name'] 
    source_object = data_structure['source_object'] 
    try:
        hub_list = generate_hub_list(cursor=cursor, source=source, source_name= source_name, source_object= source_object)
    except Exception as e:
        data_structure['print2FeedbackConsole'](message=f"Failed to query hub_list: {e}")
        return

    for hub in hub_list:
        hub_name = hub[1]
        hub_id = hub[0]
        bk_list = hub[2].split(',')
        group_name = 'RDV/' + get_groupname(cursor,hub_id)

        # Query for output_dir for this hub
        if has_column(cursor, "standard_hub", "output_dir"):
            cursor.execute("SELECT output_dir FROM standard_hub WHERE Hub_Identifier = ? LIMIT 1", (hub_id,))
            result = cursor.fetchone()
            output_dir = result[0] if result and result[0] else ""
        else:
            output_dir = ""

        bk_string = ""
        for bk in bk_list:
            bk_string += f"\n\t- '{bk}'"

        source_models = generate_source_models(cursor, hub_id)
        hashkey = generate_hashkey(cursor, hub_id)
    
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "hub.txt"), "r") as f:
                command_tmp = f.read()
        except Exception as e:
            data_structure['print2FeedbackConsole'](message=f"Failed to load template hub.txt: {e}")
            return
        f.close()
        command = command_tmp.replace('@@Schema', rdv_default_schema).replace('@@SourceModels', source_models).replace('@@Hashkey', hashkey).replace('@@BusinessKeys', bk_string)
           
        # Build the full output directory
        base_model_path = model_path.replace('@@GroupName',group_name).replace('@@SourceSystem',source_name).replace('@@timestamp',generated_timestamp)
        if output_dir:
            output_dir = sanitize_output_dir(output_dir)
            full_model_path = os.path.join(base_model_path, output_dir)
        else:
            full_model_path = base_model_path
        filename = os.path.join(full_model_path, f"{hub_name}.sql")
                
        # Ensure the directory exists
        if not os.path.exists(full_model_path):
            os.makedirs(full_model_path)

        with open(filename, 'w') as f:
            f.write(command.expandtabs(2))
            if data_structure['console_outputs']:
                data_structure['print2FeedbackConsole'](message= f"Created Hub Model {hub_name}")