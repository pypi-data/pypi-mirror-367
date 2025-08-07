import argparse
import os
import json
import sys
import warnings
#ignore : RequestsDependencyWarning: Unable to find acceptable character detection dependency (chardet or charset_normalizer).
warnings.filterwarnings("ignore", message="Unable to find acceptable character detection dependency")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from coaiamodule import read_config, transcribe_audio, summarizer, tash, abstract_process_send, initial_setup, fetch_key_val
from cofuse import (
    get_comments, post_comment,
    create_session_and_save, add_trace_node_and_save,
    load_session_file,
    create_score, apply_score_to_trace,
    list_prompts, get_prompt, create_prompt, format_prompts_table, format_prompt_display,
    list_datasets, get_dataset, create_dataset, format_datasets_table,
    list_dataset_items, format_dataset_display, format_dataset_for_finetuning,
    list_traces, list_projects, create_dataset_item, format_traces_table,
    add_trace
)

EPILOG = """see: https://github.com/jgwill/coaiapy/wiki for more details."""
EPILOG1 = """
coaiacli is a command line interface for audio transcription, summarization, and stashing to Redis.

setup these environment variables:
OPENAI_API_KEY,AWS_KEY_ID,AWS_SECRET_KEY,AWS_REGION
REDIS_HOST,REDIS_PORT,REDIS_PASSWORD,REDIS_SSL

To add a new process tag, define "TAG_instruction" and "TAG_temperature" in coaia.json.

Usage:
    coaia p TAG "My user input"
    cat myfile.txt | coaia p TAG
"""

def tash_key_val(key, value,ttl=None):
    tash(key, value,ttl)
    print(f"Key: {key}  was just saved to memory.")

def tash_key_val_from_file(key, file_path,ttl=None):
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    with open(file_path, 'r') as file:
        value = file.read()
    tash_key_val(key, value,ttl)

def process_send(process_name, input_message):
    result = abstract_process_send(process_name, input_message)
    print(f"{result}")

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for audio transcription, summarization, stashing to Redis and other processTag.", 
        epilog=EPILOG,
        usage="coaia <command> [<args>]",
        prog="coaia",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command')

    # Subparser for 'tash' command
    parser_tash = subparsers.add_parser('tash',aliases="m", help='Stash a key/value pair to Redis.')
    parser_tash.add_argument('key', type=str, help="The key to stash.")
    parser_tash.add_argument('value', type=str, nargs='?', help="The value to stash.")
    parser_tash.add_argument('-F','--file', type=str, help="Read the value from a file.")
    #--ttl
    parser_tash.add_argument('-T','--ttl', type=int, help="Time to live in seconds.",default=5555)

    # Subparser for 'transcribe' command
    parser_transcribe = subparsers.add_parser('transcribe',aliases="t", help='Transcribe an audio file to text.')
    parser_transcribe.add_argument('file_path', type=str, help="The path to the audio file.")
    parser_transcribe.add_argument('-O','--output', type=str, help="Filename to save the output.")

    # Update 'summarize' subparser
    parser_summarize = subparsers.add_parser('summarize',aliases="s", help='Summarize text from stdin or a file.')
    parser_summarize.add_argument('filename', type=str, nargs='?', help="Optional filename containing text to summarize.")
    parser_summarize.add_argument('-O','--output', type=str, help="Filename to save the output.")

    # Subparser for 'p' command
    parser_p = subparsers.add_parser('p', help='Process input message with a custom process tag.')
    parser_p.add_argument('process_name', type=str, help="The process tag defined in the config.")
    parser_p.add_argument('input_message', type=str, nargs='?', help="The input message to process.")
    parser_p.add_argument('-O','--output', type=str, help="Filename to save the output.")
    parser_p.add_argument('-F', '--file', type=str, help="Read the input message from a file.")

    # Subparser for 'init' command
    parser_init = subparsers.add_parser('init', help='Create a sample config file in $HOME/coaia.json.')

    # Subparser for 'fuse' command
    parser_fuse = subparsers.add_parser('fuse', help='Manage Langfuse integrations.')
    sub_fuse = parser_fuse.add_subparsers(dest='fuse_command', help="Subcommands for Langfuse")

    parser_fuse_base = sub_fuse.add_parser('comments', help="List or post comments to Langfuse")
    parser_fuse_base.add_argument('action', choices=['list','post'], help="Action to perform.")
    parser_fuse_base.add_argument('comment', nargs='?', help="Text for comment creation.")
    
    parser_fuse_prompts = sub_fuse.add_parser('prompts', help="Manage prompts in Langfuse (list, get, create)")
    parser_fuse_prompts.add_argument('action', choices=['list','get','create'], help="Action to perform.")
    parser_fuse_prompts.add_argument('name', nargs='?', help="Prompt name.")
    parser_fuse_prompts.add_argument('content', nargs='?', help="Prompt text.")
    parser_fuse_prompts.add_argument('--json', action='store_true', help="Output in JSON format (default: table format)")
    parser_fuse_prompts.add_argument('--debug', action='store_true', help="Show debug information for pagination")
    parser_fuse_prompts.add_argument('--label', type=str, help="Specify a label to fetch.")
    parser_fuse_prompts.add_argument('--prod', action='store_true', help="Shortcut to fetch the 'production' label.")
    parser_fuse_prompts.add_argument('-c', '--content-only', action='store_true', help="Output only the prompt content.")
    parser_fuse_prompts.add_argument('-e', '--escaped', action='store_true', help="Output the prompt content as a single, escaped line.")

    parser_fuse_ds = sub_fuse.add_parser('datasets', help="Manage datasets in Langfuse (list, get, create)")
    parser_fuse_ds.add_argument('action', choices=['list','get','create'], help="Action to perform.")
    parser_fuse_ds.add_argument('name', nargs='?', help="Dataset name.")
    parser_fuse_ds.add_argument('--json', action='store_true', help="Output in JSON format (default: table format)")
    parser_fuse_ds.add_argument('-oft', '--openai-ft', action='store_true', help="Format output for OpenAI fine-tuning.")
    parser_fuse_ds.add_argument('-gft', '--gemini-ft', action='store_true', help="Format output for Gemini fine-tuning.")
    parser_fuse_ds.add_argument('--system-instruction', type=str, default="You are a helpful assistant", help="System instruction for fine-tuning formats.")

    parser_fuse_sessions = sub_fuse.add_parser('sessions', help="Manage sessions in Langfuse (create, add node, view)")
    parser_fuse_sessions_sub = parser_fuse_sessions.add_subparsers(dest='sessions_action')

    parser_fuse_sessions_create = parser_fuse_sessions_sub.add_parser('create')
    parser_fuse_sessions_create.add_argument('session_id')
    parser_fuse_sessions_create.add_argument('user_id')
    parser_fuse_sessions_create.add_argument('-n','--name', default="New Session")
    parser_fuse_sessions_create.add_argument('-f','--file', default="session.yml")

    parser_fuse_sessions_add = parser_fuse_sessions_sub.add_parser('addnode')
    parser_fuse_sessions_add.add_argument('session_id')
    parser_fuse_sessions_add.add_argument('trace_id')
    parser_fuse_sessions_add.add_argument('user_id')
    parser_fuse_sessions_add.add_argument('-n','--name', default="Child Node")
    parser_fuse_sessions_add.add_argument('-f','--file', default="session.yml")

    parser_fuse_sessions_view = parser_fuse_sessions_sub.add_parser('view')
    parser_fuse_sessions_view.add_argument('-f','--file', default="session.yml")

    parser_fuse_sc = sub_fuse.add_parser('scores', aliases=['sc'], help="Manage scores in Langfuse (create or apply)")
    sub_fuse_sc = parser_fuse_sc.add_subparsers(dest='scores_action')

    parser_fuse_sc_create = sub_fuse_sc.add_parser('create')
    parser_fuse_sc_create.add_argument('score_id')
    parser_fuse_sc_create.add_argument('-n','--name', default="New Score")
    parser_fuse_sc_create.add_argument('-v','--value', type=float, default=1.0)

    parser_fuse_sc_apply = sub_fuse_sc.add_parser('apply')
    parser_fuse_sc_apply.add_argument('trace_id')
    parser_fuse_sc_apply.add_argument('score_id')
    parser_fuse_sc_apply.add_argument('-v','--value', type=float, default=1.0)

    parser_fuse_traces = sub_fuse.add_parser('traces', help="List or add traces in Langfuse")
    parser_fuse_traces.add_argument('--json', action='store_true', help="Output in JSON format (default: table format)")
    sub_fuse_traces = parser_fuse_traces.add_subparsers(dest='trace_action')

    parser_fuse_traces_add = sub_fuse_traces.add_parser('add', help='Add a new trace')
    parser_fuse_traces_add.add_argument('trace_id', help="Trace ID")
    parser_fuse_traces_add.add_argument('-s','--session', required=True, help="Session ID")
    parser_fuse_traces_add.add_argument('-u','--user', required=True, help="User ID") 
    parser_fuse_traces_add.add_argument('-n','--name', required=True, help="Trace name")
    parser_fuse_traces_add.add_argument('-d','--data', help="Additional trace data as JSON string")

    parser_fuse_projects = sub_fuse.add_parser('projects', help="List projects in Langfuse")
    parser_fuse_ds_items = sub_fuse.add_parser('dataset-items', help="Manage dataset items (create) in Langfuse")
    parser_fuse_ds_items_sub = parser_fuse_ds_items.add_subparsers(dest='ds_items_action')
    parser_ds_items_create = parser_fuse_ds_items_sub.add_parser('create')
    parser_ds_items_create.add_argument('datasetName')
    parser_ds_items_create.add_argument('-i','--input', required=True)
    parser_ds_items_create.add_argument('-e','--expected', help="Expected output")
    parser_ds_items_create.add_argument('-m','--metadata', help="Optional metadata as JSON string")

    # Subparser for 'fetch' command
    parser_fetch = subparsers.add_parser('fetch', help='Fetch a value from Redis by key.')
    parser_fetch.add_argument('key', type=str, help="The key to fetch.")
    parser_fetch.add_argument('-O', '--output', type=str, help="Filename to save the fetched value.")

    args = parser.parse_args()

    if args.command == 'init':
        initial_setup()
    elif args.command == 'p':
        if args.file:
            with open(args.file, 'r') as f:
                input_message = f.read()
        elif not sys.stdin.isatty():
            input_message = sys.stdin.read()
        elif args.input_message:
            input_message = args.input_message
        else:
            print("Error: No input provided.")
            return
        result = abstract_process_send(args.process_name, input_message)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
        else:
            print(f"{result}")
    elif args.command == 'tash' or args.command == 'm':
        if args.file:
            tash_key_val_from_file(args.key, args.file,args.ttl)
        elif args.value:
            tash_key_val(args.key, args.value,args.ttl)
        else:
            print("Error: You must provide a value or use the --file flag to read from a file.")
    elif args.command == 'transcribe' or args.command == 't':
        transcribed_text = transcribe_audio(args.file_path)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(transcribed_text)
        else:
            print(f"{transcribed_text}")
    elif args.command == 'summarize' or args.command == 's':
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        elif args.filename:
            if not os.path.isfile(args.filename):
                print(f"Error: File '{args.filename}' does not exist.")
                return
            with open(args.filename, 'r') as file:
                text = file.read()
        else:
            print("Error: No input provided.")
            return
        summary = summarizer(text)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(summary)
        else:
            print(f"{summary}")
    elif args.command == 'fetch':
        fetch_key_val(args.key, args.output)
    elif args.command == 'fuse':
        if args.fuse_command == 'comments':
            if args.action == 'list':
                print(get_comments())
            elif args.action == 'post':
                if not args.comment:
                    print("Error: comment text missing.")
                    return
                print(post_comment(args.comment))
        elif args.fuse_command == 'prompts':
            if args.action == 'list':
                prompts_data = list_prompts(debug=getattr(args, 'debug', False))
                if args.json:
                    print(prompts_data)
                else:
                    print(format_prompts_table(prompts_data))
            elif args.action == 'get':
                if not args.name:
                    print("Error: prompt name missing.")
                    return
                
                label = 'latest' # Default to latest
                if args.prod:
                    label = 'production'
                if args.label:
                    label = args.label

                prompt_data = get_prompt(args.name, label=label)

                if args.content_only or args.escaped:
                    try:
                        prompt_json = json.loads(prompt_data)
                        prompt_content = prompt_json.get('prompt', '')
                        if isinstance(prompt_content, list):
                            # Handle chat format
                            content = '\n'.join([msg.get('content', '') for msg in prompt_content if msg.get('content')])
                        else:
                            # Handle string format
                            content = prompt_content
                        
                        if args.escaped:
                            print(json.dumps(content))
                        else:
                            print(content)

                    except json.JSONDecodeError:
                        print(f"Error: Could not parse prompt data as JSON.\n{prompt_data}")
                    return

                if args.json:
                    print(prompt_data)
                else:
                    print(format_prompt_display(prompt_data))
            elif args.action == 'create':
                if not args.name or not args.content:
                    print("Error: name or content missing.")
                    return
                print(create_prompt(args.name, args.content))
        elif args.fuse_command == 'datasets':
            if args.action == 'list':
                datasets_data = list_datasets()
                if args.json:
                    print(datasets_data)
                else:
                    print(format_datasets_table(datasets_data))
            elif args.action == 'get':
                if not args.name:
                    print("Error: dataset name missing.")
                    return
                
                dataset_json = get_dataset(args.name)
                items_json = list_dataset_items(args.name)

                if args.openai_ft:
                    print(format_dataset_for_finetuning(items_json, 'openai', args.system_instruction))
                elif args.gemini_ft:
                    print(format_dataset_for_finetuning(items_json, 'gemini', args.system_instruction))
                elif args.json:
                    dataset_data = json.loads(dataset_json)
                    items_data = json.loads(items_json)
                    dataset_data['items'] = items_data
                    print(json.dumps(dataset_data, indent=2))
                else:
                    print(format_dataset_display(dataset_json, items_json))
            elif args.action == 'create':
                if not args.name:
                    print("Error: dataset name missing.")
                    return
                print(create_dataset(args.name))
        elif args.fuse_command == 'sessions':
            if args.sessions_action == 'create':
                print(create_session_and_save(args.file, args.session_id, args.user_id, args.name))
            elif args.sessions_action == 'addnode':
                print(add_trace_node_and_save(args.file, args.session_id, args.trace_id, args.user_id, args.name))
            elif args.sessions_action == 'view':
                data = load_session_file(args.file)
                print(data)
        elif args.fuse_command == 'scores' or args.fuse_command == 'sc':
            if args.scores_action == 'create':
                print(create_score(args.score_id, args.name, args.value))
            elif args.scores_action == 'apply':
                print(apply_score_to_trace(args.trace_id, args.score_id, args.value))
        elif args.fuse_command == 'traces':
            if args.trace_action == 'add':
                data = json.loads(args.data) if args.data else None
                print(add_trace(args.trace_id, args.user, args.session, args.name, data))
            else:
                traces_data = list_traces()
                if args.json:
                    print(traces_data)
                else:
                    print(format_traces_table(traces_data))
        elif args.fuse_command == 'projects':
            print(list_projects())
        elif args.fuse_command == 'dataset-items':
            if args.ds_items_action == 'create':
                md = args.metadata if args.metadata else None
                print(create_dataset_item(args.datasetName, args.input, args.expected, md))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
