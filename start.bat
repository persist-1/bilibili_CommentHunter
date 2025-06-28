@echo off
:: 设置UTF-8编码解决中文乱码问题
chcp 65001 >nul

echo 正在启动Bilibili评论爬取与分析系统...
echo.

:: 获取当前bat文件所在目录并切换到项目根目录
cd /d "%~dp0"

:: 启动后端服务
echo 启动后端服务...
start "Bilibili-CH-Backend" cmd /k "chcp 65001 >nul && api.bat"

:: 等待1秒
timeout /t 1 /nobreak >nul

:: 切换到前端目录并启动前端服务
echo 启动前端服务...
cd webui
start "Bilibili-CH-Frontend" cmd /k "chcp 65001 >nul && webui.bat"

:: 返回项目根目录
cd ..

echo.
echo 系统启动完成
echo -后端服务: http://localhost:60001
echo -前端服务: http://localhost:60002
echo.
echo 按任意键退出启动脚本...
pause >nul
exit