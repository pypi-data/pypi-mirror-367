import argparse
import base64
import json
import sys


def encode_file_to_base64(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        sys.exit(f'Failed to read or parse JSON file: {e}')

    try:
        json_string = json.dumps(data)
        encoded_bytes = base64.b64encode(json_string.encode('utf-8'))
        return encoded_bytes.decode('utf-8')
    except Exception as e:
        sys.exit(f'Encoding failed: {e}')


def decode_base64_to_json_string(encoded_str: str) -> str:
    try:
        decoded_bytes = base64.b64decode(encoded_str)
        json_obj = json.loads(decoded_bytes.decode('utf-8'))
        return json.dumps(json_obj, indent=4)
    except Exception as e:
        sys.exit(f'Decoding failed: {e}')


def main():
    parser = argparse.ArgumentParser(description='Encode or decode JSON using base64.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode a JSON file to a base64 string.')
    encode_parser.add_argument('filepath', help='Path to the JSON file.')

    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode a base64 string to formatted JSON.')
    decode_parser.add_argument('string', nargs='?', help='Base64 encoded string. If not provided, reads from stdin.')

    args = parser.parse_args()

    if args.command == 'encode':
        output = encode_file_to_base64(args.filepath)
        print(output)

    elif args.command == 'decode':
        input_string = args.string
        if input_string is None:
            input_string = sys.stdin.read().strip()
        output = decode_base64_to_json_string(input_string)
        print(output)


if __name__ == '__main__':
    main()
