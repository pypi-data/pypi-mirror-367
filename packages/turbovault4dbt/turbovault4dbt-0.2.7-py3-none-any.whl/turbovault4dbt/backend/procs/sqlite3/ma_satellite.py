from numpy import object_
import os
from turbovault4dbt.backend.procs.sqlite3.utils import has_column, sanitize_output_dir

    
def get_groupname(cursor,object_id):
    query = f"""SELECT DISTINCT GROUP_NAME from multiactive_satellite where MA_Satellite_Identifier = '{object_id}' ORDER BY Target_Column_Sort_Order LIMIT 1"""
    cursor.execute(query)
    return cursor.fetchone()[0]

def gen_payload(payload_list):
    payload_string = ''
    
    for column in payload_list:
        payload_string = payload_string + f'\t- {column.lower()}\n'
    
    return payload_string

def generate_ma_satellite_list(cursor, source, source_name, source_object):

    query = f"""SELECT DISTINCT MA_Satellite_Identifier,Target_Satellite_Table_Physical_Name,Parent_Primary_Key_Physical_Name,GROUP_CONCAT(Target_Column_Physical_Name),
                Source_Table_Physical_Name,Load_Date_Column,Multi_Active_Attributes
                from 
                (SELECT DISTINCT hs.MA_Satellite_Identifier,hs.Target_Satellite_Table_Physical_Name,hs.Parent_Primary_Key_Physical_Name,hs.Target_Column_Physical_Name,
                src.Source_Table_Physical_Name,src.Load_Date_Column,hs.Multi_Active_Attributes FROM multiactive_satellite hs
                inner join source_data src on src.Source_table_identifier = hs.Source_Table_Identifier
                where 1=1
                and src.Source_System = '{source_name}'
                and src.Source_Object = '{source_object}'
                order by Target_Column_Sort_Order asc)
                group by MA_Satellite_Identifier,Target_Satellite_Table_Physical_Name,Parent_Primary_Key_Physical_Name,Source_Table_Physical_Name,Load_Date_Column"""

    cursor.execute(query)
    results = cursor.fetchall()

    return results
        

def generate_ma_satellite(data_structure):
    cursor = data_structure['cursor']
    source = data_structure['source']
    generated_timestamp = data_structure['generated_timestamp']
    rdv_default_schema = data_structure['rdv_default_schema']
    model_path = data_structure['model_path']  
    hashdiff_naming = data_structure['hashdiff_naming']        
    source_name = data_structure['source_name'] 
    source_object = data_structure['source_object'] 
    try:
        satellite_list = generate_ma_satellite_list(cursor=cursor, source=source, source_name= source_name, source_object= source_object)
    except Exception as e:
        data_structure['print2FeedbackConsole'](message=f"Failed to query ma_satellite_list: {e}")
        return

    for satellite in satellite_list:
        satellite_name = satellite[1]
        hashkey_column = satellite[2]
        hashdiff_column = hashdiff_naming.replace('@@SatName',satellite_name)
        payload_list = satellite[3].split(',')
        source_model = satellite[4].lower()
        loaddate = satellite[5]
        ma_attribute_list = satellite[6].split(';')
        group_name = 'RDV/' + get_groupname(cursor,satellite[0])
        # Query for output_dir for this MA satellite, if the column exists
        if has_column(cursor, "multiactive_satellite", "output_dir"):
            cursor.execute(
                "SELECT output_dir FROM multiactive_satellite WHERE MA_Satellite_Identifier = ? LIMIT 1",
                (satellite[0],)
            )
            result = cursor.fetchone()
            output_dir = result[0] if result and result[0] else ""
        else:
            output_dir = ""

        # Build the full output directory for v0 and v1
        base_model_path = model_path.replace('@@GroupName',group_name).replace('@@SourceSystem',source_name).replace('@@timestamp',generated_timestamp)
        if output_dir:
            output_dir = sanitize_output_dir(output_dir)
            full_model_path = os.path.join(base_model_path, output_dir)
        else:
            full_model_path = base_model_path

        payload = gen_payload(payload_list)
        ma_attribute = gen_payload(ma_attribute_list)

        # Satellite_v0
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "ma_sat_v0.txt"), "r") as f:
                command_tmp = f.read()
        except Exception as e:
            data_structure['print2FeedbackConsole'](message=f"Failed to load template ma_sat_v0.txt: {e}")
            return
        command_v0 = command_tmp.replace('@@SourceModel', source_model).replace('@@Hashkey', hashkey_column).replace('@@Hashdiff', hashdiff_column).replace('@@MaAttribute', ma_attribute).replace('@@Payload', payload).replace('@@LoadDate', loaddate).replace('@@Schema', rdv_default_schema)

        satellite_model_name_splitted_list = satellite_name.split('_')
        if len(satellite_model_name_splitted_list) >= 2:
            satellite_model_name_splitted_list[-2] += '0'
            satellite_model_name_v0 = '_'.join(satellite_model_name_splitted_list)
        else:
            satellite_model_name_v0 = satellite_name + '0'
            data_structure['print2FeedbackConsole'](
                message=f"Satellite name '{satellite_name}' does not have enough '_' segments, used fallback name '{satellite_model_name_v0}'"
            )

        filename = os.path.join(full_model_path, f"{satellite_model_name_v0}.sql")
        if not os.path.exists(full_model_path):
            os.makedirs(full_model_path)
        with open(filename, 'w') as f:
            f.write(command_v0.expandtabs(2))
            if data_structure['console_outputs']:
                data_structure['print2FeedbackConsole'](message= f"Created Multi Active Satellite Model {satellite_model_name_v0}")

        # Satellite_v1
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "ma_sat_v1.txt"), "r") as f:
                command_tmp = f.read()
        except Exception as e:
            data_structure['print2FeedbackConsole'](message=f"Failed to load template ma_sat_v1.txt: {e}")
            return
        command_v1 = command_tmp.replace('@@SatName', satellite_model_name_v0).replace('@@Hashkey', hashkey_column).replace('@@Hashdiff', hashdiff_column).replace('@@MaAttribute', ma_attribute).replace('@@LoadDate', loaddate).replace('@@Schema', rdv_default_schema)

        filename_v1 = os.path.join(full_model_path, f"{satellite_name}.sql")
        if not os.path.exists(full_model_path):
            os.makedirs(full_model_path)
        with open(filename_v1, 'w') as f:
            f.write(command_v1.expandtabs(2))
            if data_structure['console_outputs']:
                data_structure['print2FeedbackConsole'](message= f"Created Multi Active Satellite Model {satellite_name}")