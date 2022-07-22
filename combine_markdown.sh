#!/bin/bash

MARKDOWN_FILES="markdown_files/*"
ALL_DISCOVERIES="ALL_DISCOVERIES.md"
MD_TEMPLATE="md_template.md"

cat "${MD_TEMPLATE}" > "${ALL_DISCOVERIES}"
cat ${MARKDOWN_FILES} >> "${ALL_DISCOVERIES}"

