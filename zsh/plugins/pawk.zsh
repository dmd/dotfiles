pawk(){
    fields="$(sed -E 's/(^|,)/ \1\$/g'<<<"$1")"
    shift
    awk "{print $fields}" "$@"
}
