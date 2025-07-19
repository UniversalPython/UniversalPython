def argos_translator(text, source):
        if not argos_translate_initialized:
            initialize_argos_translate()

        if argos_translator is not None:
            try:
                return argos_translator.translate(text)
            except Exception as e:
                print(f"Warning: Translation failed - {str(e)}")
                return text
        return text