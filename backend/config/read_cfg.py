import configargparse
import sys
from pathlib import Path
from os.path import join as opj

PROJECT_ROOT = Path(__file__).absolute().parents[1].absolute()
sys.path.insert(0, str(PROJECT_ROOT))

CFG_PATH: str = opj(PROJECT_ROOT, 'config', 'config.ini')


def read_cfg() -> configargparse.Namespace:
    parser = configargparse.ArgParser(description='Configuration for the server')
    parser.add_argument('-c', '--config', is_config_file=True,
                        help='config file path', default='./config/config.ini')
    parser.add_argument('--origins', nargs='+', help='List of allowed origins', required=True)
    parser.add_argument('--model_path', help='Path of the model')
    parser.add_argument('--bot_type', help='Type of the bot')
    args = parser.parse_args()

    return args


ARGS = read_cfg()
