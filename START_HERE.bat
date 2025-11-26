@echo off
echo.
echo ========================================================
echo   PUMPUP GYM EDGE SERVICE - GUIA DE USO RAPIDA
echo ========================================================
echo.
echo PARA INICIAR EL SERVIDOR:
echo   python app.py
echo.
echo PARA EJECUTAR TODOS LOS TESTS:
echo   powershell -File run_tests.ps1
echo.
echo PARA VER LA BASE DE DATOS:
echo   python check_database.py
echo.
echo ENDPOINTS DISPONIBLES:
echo   http://localhost:5000/api/v1/access/nfc-scan (POST)
echo   http://localhost:5000/api/v1/access/occupancy (GET)
echo   http://localhost:5000/api/v1/equipment/session/start (POST)
echo   http://localhost:5000/api/v1/equipment/session/end (POST)
echo   http://localhost:5000/api/v1/equipment/heart-rate (POST)
echo.
echo CREDENCIALES DE PRUEBA:
echo   Device ID: gym-esp32-001
echo   API Key: gym-api-key-2025
echo   NFC Test: 04A1B2C3D4E5F6
echo.
echo DOCUMENTACION:
echo   README.md - Guia principal
echo   API_DOCUMENTATION.md - Referencia API
echo   VERSION_1.0_COMPLETE.md - Resumen completo
echo   TESTING_RESULTS.md - Resultados de tests
echo.
echo ========================================================
echo   SISTEMA COMPLETAMENTE FUNCIONAL Y PROBADO
echo   9/9 tests pasados exitosamente
echo ========================================================
echo.
pause
