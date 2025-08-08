if __name__ == "__main__":
    from .main import main
    import sys
    main(
        config_path=sys.argv[1] if len(sys.argv) > 1 else 'api_config.json',
        is_string=(sys.argv[2].lower() == 'true') if len(sys.argv) > 2 else False
    )
