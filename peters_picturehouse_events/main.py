from .classes.movie_data_capture import MovieDataCapture
from .classes.movie_auto_processor import MovieAutoProcessor
from common.style import Colour


def main():
    movie_data = MovieDataCapture()
    movie_data.get_event_date()
    movie_data.get_movie_title()
    movie_data.get_movie_year()

    MovieAutoProcessor(movie_data)

    print(f"\n{Colour.GREEN}Build complete!{Colour.RESET}\n")


if __name__ == "__main__":
    main()
