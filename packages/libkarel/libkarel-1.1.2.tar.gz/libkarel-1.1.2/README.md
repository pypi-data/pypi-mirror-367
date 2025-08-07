# Libkarel

Utilerías en Python para validar casos de prueba de Karel.

## 🚀 Cómo contribuir

Si deseas modificar **libkarel**, sigue estos pasos para trabajar con tu propia versión del código.  

### 1️⃣ **Hacer un fork del repositorio**

Ve al repositorio oficial en GitHub:
🔗 [https://github.com/omegaup/libkarel](https://github.com/omegaup/libkarel)  

Haz clic en el botón **"Fork"** en la esquina superior derecha para crear tu propia copia del repositorio en tu cuenta.  

### 2️⃣ **Clonar el fork en tu máquina**

Una vez que tengas el fork, clónalo en tu computadora con:

```bash
git clone https://github.com/TU-USUARIO/libkarel.git
```

⚠️ **No olvides reemplazar `TU-USUARIO` con tu nombre de usuario de GitHub.**  

Luego, entra en la carpeta del proyecto:

```bash
cd libkarel
```

### 3️⃣ **Configurar el repositorio remoto**

Para mantener tu fork actualizado con el repositorio original, agrégalo como **remoto upstream**:

```bash
git remote add upstream https://github.com/omegaup/libkarel.git
```

Cada vez que quieras sincronizar cambios del repositorio oficial, usa:

```bash
git fetch upstream
git merge upstream/master
```

---

## 🛠 Prerrequisitos

Antes de instalar **libkarel**, asegúrate de contar con las siguientes herramientas en tu sistema:

### Dependencias necesarias

1. **Python 3.6 o superior**

   - Verifica tu versión con:

     ```bash
     python3 --version
     ```

   - Si necesitas instalar Python, sigue las instrucciones oficiales en [python.org](https://www.python.org/).  

2. **pip (gestor de paquetes de Python)**  
   - Si `pip` no está instalado, puedes instalarlo con:

     ```bash
     sudo apt install python3-pip
     ```

3. **pytest (para ejecutar pruebas)**  
   - Instala `pytest` con:

     ```bash
     pip install pytest
     ```

4. **Git (para gestionar el código fuente)**  
   - Si `git` no está instalado, agrégalo con:

     ```bash
     sudo apt install git
     ```

---

## 🔧 Instalación

Para instalar `libkarel` en modo desarrollo, usa:

```bash
pip install -e .
```

## ✅ Pruebas

Para ejecutar las pruebas:

```bash
cd tests
python3 -m pytest .
```

Hay algunas pruebas que se saltaron desde la configuración. Para poder ejecutarlas debes utilizar el siguiente comando:

```bash
cd tests
python3 kareltest_test.py test_case_1
```

## 🚀 Últimos cambios

- Compatibilidad con **ReKarel** (versión 1.1)  
- Nueva funcionalidad: **memoriastack**  
- Nueva funcionalidad: **llamadaMaxima**  
