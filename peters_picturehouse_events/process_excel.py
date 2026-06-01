from .classes.movie_builder import MovieBuilder
from common.style import Colour


def main():
    movie_builder = MovieBuilder()
    movie_builder.build()
    print(f"\n{Colour.GREEN}Build complete!{Colour.RESET}\n")


if __name__ == "__main__":
    main()
