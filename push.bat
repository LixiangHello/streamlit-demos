@REM 定位到仓库位置
cd /d %~dp0

@REM 添加
git add .

@REM 提交
git commit -m "Auto commit: %date% %time%"

@REM 推送到远端代码仓库
git push -u origin main

pause