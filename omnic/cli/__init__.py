from omnic import singletons


def main():
    action, args = singletons.cli.parse_args_to_action_args()
    action(args)
