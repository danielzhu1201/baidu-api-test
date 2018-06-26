name="asrocr"

py_path="/opt/virtualenv/${name}/bin/python"
echo $py_path

log_path="log"
if [ ! -d "${log_path}" ]; then
  mkdir "${log_path}"
fi

dd=`date -d "now" +%Y%m`

`nohup ${py_path} bin/start.py 1>${log_path}crontab_asr.${dd}.log 2>&1 &`
