from .classes.match_builder import MatchBuilder
from common.style import Colour


def main():
    match_builder = MatchBuilder()
    match_builder.build_events()
    print(f"\n{Colour.GREEN}Build complete!{Colour.RESET}\n")


if __name__ == "__main__":
    main()
