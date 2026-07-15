cd controlpanel
nim c --app:lib -d:release --out:controlpanel.so main.nim
cd ..
mv ./controlpanel/controlpanel.so ./back/controlpanel.so