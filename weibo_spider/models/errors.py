# @FILENAME : custom_error
# @AUTHOR : lonsty
# @DATE : 2020/3/28 18:01


class CookiesExpiredException(Exception):
    pass


class NoImagesException(Exception):
    pass


class ContentParserError(Exception):
    pass
