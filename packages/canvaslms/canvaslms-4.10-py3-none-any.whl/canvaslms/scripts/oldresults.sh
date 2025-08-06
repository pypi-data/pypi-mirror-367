#!/bin/bash

current_courses="tilkry25"
cached_results="/tmp/oldresults.cache"
course_prefixes="(tilkry|prg[im]|vetcyb)"
results() {
  if [ ! -s "${cached_results}" ]; then
    canvaslms submissions -c "${course_prefixes}" -l > "${cached_results}"
  fi
  cat "${cached_results}"
}
newest_grade() {
  student=$1
  course=$2
  assgn=$3
  grades=$(results \
           | grep "${course}" \
           | grep "${student}" \
           | grep "${assgn}")
  newest=$(echo "${grades}" \
           | sort -u -k 6 \
           | tail -n 1)
  echo "${newest}" | cut -f 4
}

main() {
  for course in ${current_courses}; do
    for student in $(canvaslms users -sc "${course}" | cut -f 2); do
      grades=$(canvaslms submissions -c tilkry2[012] -u $student | cut -f 2,4 | sort 
      -u)
      IFS=$'\n'
      if [ -z "$grades" ]; then
          continue
      fi
      for grade in $grades; do
          assgn=$(echo "$grade" | cut -f 1 -d $'\t')
          grade=$(echo "$grade" | cut -f 2 -d $'\t')
          if [ -z "$grade" ]; then
              continue
          fi
          echo $student $assgn $grade
          #canvaslms grade -c tilkry24 -a "$assgn" -g "$grade" -u $student -m 
          #"Result from previous year."
      done
    done
  done
}

# run main if not sourced
if [ "$0" = "${BASH_SOURCE}" ]; then
  main
fi
