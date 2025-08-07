from datetime import datetime
from pathlib import Path

import sys
import argparse
import logging

from amqmonitoring.client import AMQPListener
from amqmonitoring.reader import FindInDictValues, SimplePrinter


def arg_parser():
    parser = argparse.ArgumentParser(
        prog='amqmonitoring',
        description='Monitor AMQP traces')

    parser.add_argument('-f', '--find-by-dict',
                        help="Path to the json instructions",
                        dest="instructions_path", required=False, default=None)
    parser.add_argument('-s', '--store',
                        help="Path where the JSON messages"
                             " outputs will be stored",
                        required=False, default='results')
    parser.add_argument('-q', '--queue',
                        help="Name of the queue to listen",
                        required=False, default='trace')

    return parser.parse_args()

def main():
    start_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"AMQP_Traces_{start_date}"

    args = arg_parser()
    storage_path = Path(args.store)
    storage_path.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)-8s: %(message)s',
        filename=storage_path / f"{file_name}.log",
    )

    # set up logging to console
    console = logging.StreamHandler(stream=sys.stderr)
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    logger = logging.getLogger(__name__)

    # Configuration
    rabbitmq_host = 'localhost'  # Change this to your RabbitMQ host
    queue_name = 'trace'  # Change this to your queue name


    if args.instructions_path:
        # Init finder processor.
        processor = FindInDictValues(
            path_to_instructions=Path(args.instructions_path),
            json_path=Path(args.store) / f"{file_name}.json",
        )
    else:
        processor = SimplePrinter(
            json_path=Path(args.store) / f"{file_name}.json")

    # Create and start the listener
    listener = AMQPListener(host=rabbitmq_host, queue_name=queue_name)
    listener.connect()

    try:
        listener.start_listening(callback=processor.process_message)
    finally:
        processor.save_traces()


if __name__ == '__main__':
    main()
