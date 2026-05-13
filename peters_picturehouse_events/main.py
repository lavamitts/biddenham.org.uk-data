from .classes.movie_builder import MovieBuilder


def main():
    movie_builder = MovieBuilder()
    movie_builder.build()
    movie_builder.compile_archive()
    movie_builder.compile_current()
    movie_builder.build_events_csv()
    print("Build complete")


if __name__ == "__main__":
    main()
