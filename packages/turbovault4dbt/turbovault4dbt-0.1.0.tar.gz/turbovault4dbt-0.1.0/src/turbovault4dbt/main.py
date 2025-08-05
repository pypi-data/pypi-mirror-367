import sys
import os
import argparse
from turbovault4dbt.backend.excel import Excel
from turbovault4dbt.backend.config.config import MetadataInputConfig
from turbovault4dbt.backend.graph_utils import build_dependency_graph, select_nodes, print_graph
import turbovault4dbt.debuowanie as debugowanie

def print2FeedbackConsole(message):
    print(message)

def resolve_graph_and_nodes(excel_path, selectors):
    if not os.path.isfile(excel_path):
        print(f"File not found: {excel_path}")
        sys.exit(1)
    config_data = MetadataInputConfig().data['config']
    excel_config = dict(config_data['Excel'])
    excel_config['excel_path'] = excel_path
    G = build_dependency_graph(excel_path)
    if selectors:
        selected_nodes = select_nodes(G, selectors)
    else:
        selected_nodes = set(G.nodes)
    return G, selected_nodes, excel_config

def main():
    parser = argparse.ArgumentParser(description="TurboVault4dbt CLI with graph selectors")
    subparsers = parser.add_subparsers(dest='command')

    # Parent parser for shared arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--file', required=True, help='Path to Excel metadata file')
    parent_parser.add_argument('-s', '--select', nargs='*', help='Selector(s) for graph nodes (e.g. +A B+ @C)')

    # Run subcommand
    run_parser = subparsers.add_parser('run', parents=[parent_parser], help='Generate output for selected nodes')
    run_parser.add_argument('--output-dir', required=False, help='Directory to write generated output files')

    # List subcommand
    list_parser = subparsers.add_parser('list', parents=[parent_parser], help='List resolved nodes for a selector')

    # Custom logic: if no subcommand or first arg is not a valid command, show help and exit
    valid_commands = {'run', 'list'}
    if len(sys.argv) <= 1 or sys.argv[1] not in valid_commands:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    G, selected_nodes, excel_config = resolve_graph_and_nodes(args.file, args.select)

    if args.command == 'list':
        print("All nodes resolved by selectors:")
        for node in selected_nodes:
            print(f"  {node}")
        return

    if args.command == 'run':
        print("Selected nodes for processing:")
        for node in selected_nodes:
            print(f"  {node}")

        # Map node types to generator tasks
        type_to_task = {
            'hub': 'Standard Hub',
            'satellite': 'Standard Satellite',
            'link': 'Standard Link',
            'nh_satellite': 'Non-Historized Satellite',
            'ma_satellite': 'Multi-Active Satellite',
            'pit': 'Point-in-Time',
            'stage': 'Stage'
        }

        # Build tasks and sources from selected nodes
        tasks = set()
        sources_to_process = []
        for node in selected_nodes:
            ntype = G.nodes[node].get('type')
            if ntype in type_to_task:
                tasks.add(type_to_task[ntype])
                sources_to_process.append(node)

        if not sources_to_process:
            print("No valid sources/entities selected for code generation.")
            sys.exit(0)

        # Set output directory if provided
        if args.output_dir:
            excel_config['output_dir'] = args.output_dir

        excel_processor = Excel(turboVaultconfigs=excel_config, print2FeedbackConsole=print2FeedbackConsole)
        excel_processor.read()
        excel_processor.setTODO(
            SourceYML=True,
            Tasks=list(tasks),
            DBDocs=False,
            Properties=False,
            Sources=sources_to_process
        )
        excel_processor.run()

if __name__ == '__main__':
    main()