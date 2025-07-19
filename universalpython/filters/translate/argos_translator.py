import warnings
from functools import lru_cache

# Global state variables
_argos_translate_initialized = False
_argos_translate_available = False
_translation_models = {}

def initialize_argos_translate(source_lang="en", target_lang="en"):
    """Initialize Argos Translate with status messages and package installation"""
    global _argos_translate_initialized, _argos_translate_available, _translation_models
    
    if _argos_translate_initialized:
        return
        
    _argos_translate_initialized = True
    
    try:
        import argostranslate.package
        import argostranslate.translate
        _argos_translate_available = True
        
        # Update package index
        print("Updating Argos Translate package index...")
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        
        # Find and install required translation package
        package_to_install = next(
            (pkg for pkg in available_packages 
             if pkg.from_code == source_lang and pkg.to_code == target_lang),
            None
        )
        
        if package_to_install:
            print(f"Installing translation package: {source_lang} -> {target_lang}")
            argostranslate.package.install_from_path(package_to_install.download())
            
            # Load the installed model
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages if lang.code == source_lang), None)
            to_lang = next((lang for lang in installed_languages if lang.code == target_lang), None)
            
            if from_lang and to_lang:
                _translation_models[(source_lang, target_lang)] = from_lang.get_translation(to_lang)
                print("Translation package installed successfully.")
            else:
                warnings.warn("Failed to load installed languages.")
        else:
            warnings.warn(f"No translation package available for {source_lang} -> {target_lang}")
            
    except ImportError:
        warnings.warn("Argos Translate not available. Install with: pip install argostranslate")
        _argos_translate_available = False
    except Exception as e:
        warnings.warn(f"Failed to initialize Argos Translate: {str(e)}")
        _argos_translate_available = False

@lru_cache(maxsize=1000)
def argos_translator(text, source_lang="en"):
    """Translate text using Argos Translate with lazy initialization"""
    target_lang = "en"  # We always translate to English
    
    if not _argos_translate_initialized:
        initialize_argos_translate(source_lang, target_lang)
    
    if not _argos_translate_available:
        return text
        
    try:
        # Check if we have a cached model
        if (source_lang, target_lang) not in _translation_models:
            # Try to load existing installed model
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages if lang.code == source_lang), None)
            to_lang = next((lang for lang in installed_languages if lang.code == target_lang), None)
            
            if from_lang and to_lang:
                _translation_models[(source_lang, target_lang)] = from_lang.get_translation(to_lang)
            else:
                warnings.warn(f"No translation model available for {source_lang} -> {target_lang}")
                return text
        
        # Perform the translation
        translation_model = _translation_models[(source_lang, target_lang)]
        translated_text = translation_model.translate(text)
        return translated_text
        
    except Exception as e:
        warnings.warn(f"Translation failed for '{text}': {str(e)}")
        return text