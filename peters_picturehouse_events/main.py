from .classes.movie_builder import MovieBuilder


def main():
    movie_builder = MovieBuilder()
    movie_builder.build()
    print("Build complete")


if __name__ == "__main__":
    main()
