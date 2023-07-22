from googletrans import Translator

languages = []

translator = Translator()


def translation(first, second, *args):
    list_to_translate = list(args)
    translations = translator.translate(list_to_translate, src=first, dest=second)
    return translations[0]


print(translation("en", "ru", ["start"]))