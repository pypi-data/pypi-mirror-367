import sys
import os
import argparse
import glob
import pandas as pd
from turbovault4dbt.backend.excel import Excel
from turbovault4dbt.backend.csv import CSV  # <-- Import CSV processor
from turbovault4dbt.backend.config.config import MetadataInputConfig
from turbovault4dbt.backend.graph_utils import build_dependency_graph, select_nodes, build_dependency_graph_from_csvs, print_graph

def print2FeedbackConsole(message):
    print(message)

def resolve_graph_and_nodes(input_path, selectors, input_format):
    config_data = MetadataInputConfig().data['config']
    excel_config = dict(config_data['Excel'])
    excel_config['input_path'] = input_path
    excel_config['input_format'] = input_format

    # Error handling for input
    if input_format in ['xls', 'xlsx']:
        if not os.path.isfile(input_path) or not input_path.lower().endswith(('.xls', '.xlsx')):
            print(f"Error: Excel file not found or invalid: {input_path}")
            sys.exit(1)
        G = build_dependency_graph(input_path)
    elif input_format == 'csv':
        if not os.path.isdir(input_path):
            print(f"Error: CSV folder not found: {input_path}")
            sys.exit(1)
        csv_files = glob.glob(os.path.join(input_path, '*.csv'))
        if not csv_files:
            print(f"Error: No CSV files found in folder: {input_path}")
            sys.exit(1)
        # Read all CSVs into a dict of DataFrames
        sheet_dfs = {os.path.splitext(os.path.basename(f))[0]: pd.read_csv(f) for f in csv_files}
        G = build_dependency_graph_from_csvs(sheet_dfs)
        excel_config['csv_sheets'] = sheet_dfs
    else:
        print("Error: Unsupported format. Use 'xls' or 'csv'.")
        sys.exit(1)

    if selectors:
        selected_nodes = select_nodes(G, selectors)
    else:
        selected_nodes = set(G.nodes)
    return G, selected_nodes, excel_config

def main():
    parser = argparse.ArgumentParser(description="TurboVault4dbt CLI with graph selectors and flexible input format")
    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser('run', help='Generate output for selected nodes')
    list_parser = subparsers.add_parser('list', help='List resolved nodes for a selector')

    for subparser in [run_parser, list_parser]:
        subparser.add_argument('-f', '--format', required=True, choices=['xls', 'xlsx', 'csv'], help='Input format')
        subparser.add_argument('input', help='Path to Excel file or folder of CSV files')
        subparser.add_argument('-s', '--select', nargs='*', help='Selector(s) for graph nodes')
        subparser.add_argument('--output-dir', required=False, help='Directory to write generated output files')


    # Custom logic: if no subcommand or first arg is not a valid command, show help and exit
    # valid_commands = {'run', 'list'}
    # if len(sys.argv) <= 1 or sys.argv[1] not in valid_commands:
    #     parser.print_help()
    #     sys.exit(1)

    args = parser.parse_args()

    G, selected_nodes, excel_config = resolve_graph_and_nodes(args.input, args.select, args.format)

    if args.command == 'list':
        print("All nodes resolved by selectors:")
        for node in selected_nodes:
            print(f"  {node}")
        return

    if args.command == 'run':
        print("Selected nodes for processing:")
        for node in selected_nodes:
            print(f"  {node}")

        type_to_task = {
            'hub': 'Standard Hub',
            'satellite': 'Standard Satellite',
            'link': 'Standard Link',
            'nh_satellite': 'Non-Historized Satellite',
            'ma_satellite': 'Multi-Active Satellite',
            'pit': 'Point-in-Time',
            'stage': 'Stage'
        }

        tasks = set()
        sources_to_process = []
        valid_types_for_source_data = ['hub', 'satellite', 'link', 'ma_satellite', 'nh_satellite']

        for node in selected_nodes:
            ntype = G.nodes[node].get('type')
            if ntype in type_to_task:
                tasks.add(type_to_task[ntype])
                if ntype in valid_types_for_source_data and '_hub' not in node:
                    sources_to_process.append(node)

        if not sources_to_process:
            print("No valid sources/entities selected for code generation.")
            sys.exit(0)

        if args.output_dir:
            excel_config['output_dir'] = args.output_dir

        # Instantiate the correct processor based on format
        if args.format in ['xls', 'xlsx']:
            processor = Excel(turboVaultconfigs=excel_config, print2FeedbackConsole=print2FeedbackConsole)
        elif args.format == 'csv':
            processor = CSV(turboVaultconfigs=excel_config, print2FeedbackConsole=print2FeedbackConsole)
        else:
            print("Error: Unsupported format. Use 'xls' or 'csv'.")
            sys.exit(1)

        processor.read()
        processor.setTODO(
            SourceYML=True,
            Tasks=list(tasks),
            DBDocs=False,
            Properties=False,
            Sources=sources_to_process
        )
        processor.run()

if __name__ == '__main__':
    main()