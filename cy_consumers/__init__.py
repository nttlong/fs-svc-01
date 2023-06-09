"""
This library is a system of Consumer run with below work flow: \n

MSG_FILE_UPLOAD \n
├── MSG_FILE_GENERATE_IMAGE_FROM_VIDEO \n
│   ├── MSG_FILE_GENERATE_PDF_FROM_IMAGE \n
│   │   └── MSG_FILE_OCR_CONTENT \n
│   │       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE \n
│   └── MSG_FILE_GENERATE_THUMBS \n
│       ├── MSG_FILE_SAVE_DEFAULT_THUMB \n
│       └── MSG_FILE_SAVE_CUSTOM_THUMB \n
├── MSG_FILE_EXTRACT_TEXT_FROM_VIDEO \n
├── MSG_FILE_GENERATE_IMAGE_FROM_OFFICE \n
│   └── MSG_FILE_GENERATE_THUMBS \n
│       ├── MSG_FILE_SAVE_DEFAULT_THUMB \n
│       └── MSG_FILE_SAVE_CUSTOM_THUMB \n
├── MSG_FILE_GENERATE_IMAGE_FROM_PDF \n
│   └── MSG_FILE_OCR_CONTENT \n
│       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE \n
├── MSG_FILE_GENERATE_PDF_FROM_IMAGE \n
│   └── MSG_FILE_OCR_CONTENT \n
│       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE \n
├── MSG_FILE_GENERATE_THUMBS \n
│   ├── MSG_FILE_SAVE_DEFAULT_THUMB \n
│   └── MSG_FILE_SAVE_CUSTOM_THUMB \n
└── MSG_FILE_OCR_CONTENT \n
    └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE \n


"""