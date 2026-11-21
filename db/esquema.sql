-- Tabla de usuarios del sistema
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    clave_hash TEXT NOT NULL,
    nombre TEXT,
    rol TEXT DEFAULT 'analista',
    creado_en TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Archivos que sube cada usuario
CREATE TABLE IF NOT EXISTS cargas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nombre_archivo TEXT NOT NULL,
    filas INTEGER,
    filas_descartadas INTEGER,
    creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Resultados de los modelos (pronostico y riesgo de quiebre)
CREATE TABLE IF NOT EXISTS analisis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    carga_id INTEGER,
    tipo TEXT NOT NULL,          -- 'pronostico' o 'riesgo'
    sku TEXT,
    tienda TEXT,
    resultado REAL,
    detalle TEXT,                -- JSON con info extra
    nota TEXT,                   -- comentario editable del usuario
    creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (carga_id) REFERENCES cargas(id) ON DELETE SET NULL
);
