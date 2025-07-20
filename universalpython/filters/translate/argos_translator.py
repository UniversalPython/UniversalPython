import warnings
from functools import lru_cache

# Global state variables
_argos_translate_initialized = False
_argos_translate_available = False
_translation_models = {}
_verbose = False  # Control output verbosity

def set_verbose_mode(enabled: bool):
    """Control whether initialization messages should be shown"""
    global _verbose
    _verbose = enabled

def _log(message: str):
    """Conditional logging based on verbosity"""
    if _verbose:
        print(message)

def initialize_argos_translate(source_lang="en", target_lang="en"):
    """Initialize Argos Translate with silent package installation"""
    global _argos_translate_initialized, _argos_translate_available, _translation_models
    
    if _argos_translate_initialized:
        return
        
    _argos_translate_initialized = True
    
    try:
        import argostranslate.package
        import argostranslate.translate
        _argos_translate_available = True
        
        # Silently update package index
        _log("Updating Argos Translate package index...")
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        
        # Find required translation package
        package_to_install = next(
            (pkg for pkg in available_packages 
             if pkg.from_code == source_lang and pkg.to_code == target_lang),
            None
        )
        
        if package_to_install:
            _log(f"Installing translation package: {source_lang} -> {target_lang}")
            argostranslate.package.install_from_path(package_to_install.download())
            
            # Load the installed model
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages if lang.code == source_lang), None)
            to_lang = next((lang for lang in installed_languages if lang.code == target_lang), None)
            
            if from_lang and to_lang:
                _translation_models[(source_lang, target_lang)] = from_lang.get_translation(to_lang)
                _log("Translation package installed successfully.")
            else:
                warnings.warn("Failed to load installed languages.", RuntimeWarning)
        else:
            warnings.warn(f"No translation package available for {source_lang} -> {target_lang}", RuntimeWarning)
            
    except ImportError:
        warnings.warn("Argos Translate not available. Install with: pip install argostranslate", RuntimeWarning)
        _argos_translate_available = False
    except Exception as e:
        warnings.warn(f"Failed to initialize Argos Translate: {str(e)}", RuntimeWarning)
        _argos_translate_available = False

@lru_cache(maxsize=1000)
def argos_translator(text, source_lang="en"):
    """Translate text using Argos Translate with silent initialization"""
    target_lang = "en"  # We always translate to English
    
    if not _argos_translate_initialized:
        initialize_argos_translate(source_lang, target_lang)
    
    if not _argos_translate_available:
        return text
        
    try:
        # Check if we have a cached model
        if (source_lang, target_lang) not in _translation_models:
            # Try to load existing installed model
            import argostranslate.translate
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages if lang.code == source_lang), None)
            to_lang = next((lang for lang in installed_languages if lang.code == target_lang), None)
            
            if from_lang and to_lang:
                _translation_models[(source_lang, target_lang)] = from_lang.get_translation(to_lang)
            else:
                warnings.warn(f"No translation model available for {source_lang} -> {target_lang}", RuntimeWarning)
                return text
        
        # Perform the translation
        translation_model = _translation_models[(source_lang, target_lang)]
        return translation_model.translate(text)
        
    except Exception as e:
        warnings.warn(f"Translation failed for '{text[:20]}...': {str(e)}", RuntimeWarning)
        return text