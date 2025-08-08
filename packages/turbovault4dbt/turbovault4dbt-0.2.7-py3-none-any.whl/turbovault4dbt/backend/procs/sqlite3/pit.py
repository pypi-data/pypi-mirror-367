import os
from turbovault4dbt.backend.procs.sqlite3.utils import has_column, sanitize_output_dir


def get_groupname(cursor,object_id):
    query = f"""SELECT DISTINCT GROUP_NAME from pit where Pit_Identifier = '{object_id}' LIMIT 1"""
    cursor.execute(query)
    return cursor.fetchone()[0]

def get_sat_names(cursor,sat_ids):
    sat_names = []
    
    for id in sat_ids:
        query = f"""SELECT DISTINCT Target_Satellite_Table_Physical_Name from standard_satellite where Satellite_Identifier = '{id}'"""
        cursor.execute(query)
        sat_names.append(cursor.fetchone()[0])

    return sat_names

def get_pit_list(cursor, source_name, source_object):

    query = f"""SELECT 
    p.Pit_Identifier
    ,p.Pit_Physical_Table_Name
    ,h.Target_Hub_table_physical_name
    ,h.Target_Primary_Key_Physical_Name
    ,p.Satellite_Identifiers
    ,COALESCE(p.Snapshot_Model_Name,'control_snap_v1')
    ,COALESCE(p.Snapshot_Trigger_Column,'is_active')
    ,COALESCE(p.Dimension_Key_Name
    ,REPLACE(h.Target_Primary_Key_Physical_Name,'_h','_d'))
    FROM pit p
    inner join standard_hub h on p.Tracked_Entity = h.Hub_Identifier
    inner join source_data src on h.Source_table_identifier = src.Source_table_identifier
    WHERE 1=1
    and src.Source_System = '{source_name}'
    and src.Source_Object = '{source_object}'
    
    UNION

    SELECT p.Pit_Identifier, p.Pit_Physical_Table_Name,l.Target_Link_table_physical_name,l.Target_Primary_Key_Physical_Name,p.Satellite_Identifiers
    ,COALESCE(p.Snapshot_Model_Name,'control_snap_v1'),COALESCE(p.Snapshot_Trigger_Column,'is_active')
    ,COALESCE(p.Dimension_Key_Name, REPLACE(l.Target_Primary_Key_Physical_Name,'_l','_d'))
    FROM pit p
    inner join standard_link l on p.Tracked_Entity = l.Link_Identifier
    inner join source_data src on l.Source_table_identifier = src.Source_table_identifier
    WHERE 1=1
    and src.Source_System = '{source_name}'
    and src.Source_Object = '{source_object}'
    """

    cursor.execute(query)
    results = cursor.fetchall() 
    return results

def generate_pit(data_structure):
    cursor = data_structure['cursor']
    source = data_structure['source']
    generated_timestamp = data_structure['generated_timestamp']
    model_path = data_structure['model_path']   
    source_name = data_structure['source_name'] 
    source_object = data_structure['source_object'] 
    pit_list = get_pit_list(cursor=cursor, source_name= source_name, source_object= source_object)
    
    sat_names = ''
    tracked_entity = ''
    pk = ''
    snapshot_model_name = ''
    snapshot_trigger_column = ''
    dimension_key_name = ''
    pit_name = ''

    for pit in pit_list:
        pit_name = pit[1]
        tracked_entity = pit[2]
        pk = pit[3]
        satellites = pit[4]
        snapshot_model_name = pit[5]
        snapshot_trigger_column = pit[6]
        dimension_key_name = pit[7]
        sat_ids = satellites.split(';')
        sat_names = get_sat_names(cursor=cursor, sat_ids=sat_ids)
        group_name = 'BDV/' + get_groupname(cursor, pit[0])

        # --- Query for output_dir for this PIT ---
        if has_column(cursor, "pit", "output_dir"):
            cursor.execute("SELECT output_dir FROM pit WHERE Pit_Identifier = ? LIMIT 1", (pit[0],))
            result = cursor.fetchone()
            output_dir = result[0] if result and result[0] else ""
        else:
            output_dir = ""


        # --- Build the full output directory for PIT model ---
        base_model_path_v1 = model_path.replace('@@GroupName', group_name).replace('@@SourceSystem', source_name).replace('@@timestamp', generated_timestamp)
        if output_dir:
            output_dir = sanitize_output_dir(output_dir)
            full_model_path_v1 = os.path.join(base_model_path_v1, output_dir)
        else:
            full_model_path_v1 = base_model_path_v1

        all_satellite_names = ''
        for sat in sat_names:
            all_satellite_names += f"\n\t- {sat}"

        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "pit_v1.txt"), "r") as f:
                command_tmp = f.read()
        except Exception as e:
            data_structure['print2FeedbackConsole'](message=f"Failed to load template pit_v1.txt: {e}")
            return
        command = command_tmp.replace('@@TrackedEntity', tracked_entity).replace('@@PK', pk).replace('@@SnapshotModelName', snapshot_model_name).replace('@@SnapshotTriggerColumn', snapshot_trigger_column).replace('@@DimensionKey', dimension_key_name).replace('@@SatNames', all_satellite_names)

        if sat_names != '':
            filename = os.path.join(full_model_path_v1, f"{pit_name}.sql")
            if not os.path.exists(full_model_path_v1):
                os.makedirs(full_model_path_v1)
            with open(filename, 'w') as f:
                f.write(command.expandtabs(2))
            if data_structure['console_outputs']:
                data_structure['print2FeedbackConsole'](message=f"Created Pit Model {pit_name}")

            # --- Control Snapshots (unchanged, but you can add similar output_dir logic if needed) ---
            # control_snap_v0
            try:
                with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "control_snap_v0.txt")) as f1:
                    control_snap_v0 = f1.read()
            except Exception as e:
                data_structure['print2FeedbackConsole'](message=f"Failed to load template control_snap_v0.txt: {e}")
                return
            filename_snap1 = os.path.join(model_path_control, f"control_snap_v0.sql")
            if not os.path.exists(model_path_control):
                os.makedirs(model_path_control)
            with open(filename_snap1, 'w') as f:
                f.write(control_snap_v0.expandtabs(2))

            # control_snap_v1
            try:
                with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "control_snap_v1.txt")) as f1:
                    control_snap_v1 = f1.read()
            except Exception as e:
                data_structure['print2FeedbackConsole'](message=f"Failed to load template control_snap_v1.txt: {e}")
                return
            filename_snap0 = os.path.join(model_path_control, f"control_snap_v1.sql")
            if not os.path.exists(model_path_control):
                os.makedirs(model_path_control)
            with open(filename_snap0, 'w') as f:
                f.write(control_snap_v1.expandtabs(2))



