-- Ver datos completos de personas con sus participantes
SELECT p.*, pt.nidparticipant, pt.isactive as participante_activo
FROM s02person p
LEFT JOIN s02participant pt ON p.nidperson = pt.nidperson
ORDER BY p.tcreatedat DESC;
SELECT 
    CASE WHEN isactive THEN 'Activos' ELSE 'Inactivos' END as estado,
    count(*) as total
FROM s02participant GROUP BY isactive;



-- Ver equipos con sus miembros
SELECT wt.nidworkshopteam, wt.cteamname, wt.nidworkshop,
       wt.tcreatedat,
       (SELECT count(*) FROM s02workshop_team_member wtm 
        WHERE wtm.nidworkshopteam = wt.nidworkshopteam) as num_integrantes
FROM s02workshop_team wt
ORDER BY wt.tcreatedat DESC;

-- Detalle de miembros por equipo
SELECT wtm.nidworkshopteam, wt.cteamname,
       p.cfirstname, p.clastname, p.cemail
FROM s02workshop_team_member wtm
JOIN s02workshop_team wt ON wtm.nidworkshopteam = wt.nidworkshopteam
JOIN s02participant pt ON wtm.nidparticipant = pt.nidparticipant
JOIN s02person p ON pt.nidperson = p.nidperson
ORDER BY wt.cteamname, p.clastname;







-- Observaciones por tipo de iniciativa
SELECT it.cname as iniciativa, count(*) as total
FROM s03observation_log ol
JOIN s03initiative_type it ON ol.nidinitiativetype = it.nidinitiativetype
GROUP BY it.cname
ORDER BY total DESC;


-- Observaciones por fecha (agrupadas por día)
SELECT DATE(ol.tobservedat) as fecha, count(*) as total
FROM s03observation_log ol
GROUP BY DATE(ol.tobservedat)
ORDER BY fecha DESC;



-- Programas con talleres
SELECT pr.nidprogram, pr.cname as programa, 
       count(w.nidworkshop) as num_talleres
FROM s01program pr
LEFT JOIN s01workshop w ON pr.nidprogram = w.nidprogram
GROUP BY pr.nidprogram, pr.cname;


SELECT p.cfirstname || ' ' || COALESCE(p.clastname, '') as participante,
       COALESCE(SUM(CASE WHEN it.cname = 'Aceptación (A)' THEN 1 ELSE 0 END), 0) as acepta,
       COALESCE(SUM(CASE WHEN it.cname = 'Conflicto - Imposición' THEN 1 ELSE 0 END), 0) as conflicto_imposicion,
       COALESCE(SUM(CASE WHEN it.cname = 'Conflicto - Mediación' THEN 1 ELSE 0 END), 0) as conflicto_mediacion,
       COALESCE(SUM(CASE WHEN it.cname = 'Contacto Visual' THEN 1 ELSE 0 END), 0) as contacto_visual,
       COALESCE(SUM(CASE WHEN it.cname = 'Interrupción' THEN 1 ELSE 0 END), 0) as interrupcion,
       COALESCE(SUM(CASE WHEN it.cname = 'Parafraseo' THEN 1 ELSE 0 END), 0) as parafraseo,
       COALESCE(SUM(CASE WHEN it.cname = 'Propuesta (L)' THEN 1 ELSE 0 END), 0) as propuesta,
       count(ol.nidobservationlog) as total
FROM s03observation_log ol
JOIN s02participant pt ON ol.nidparticipant = pt.nidparticipant
JOIN s02person p ON pt.nidperson = p.nidperson
JOIN s03initiative_type it ON ol.nidinitiativetype = it.nidinitiativetype
GROUP BY p.cfirstname, p.clastname
ORDER BY total DESC;

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS timescaledb;

SELECT * FROM "S01BOUNDARIE" WHERE cname0 = 'Peru';


DROP TABLE "S01BOUNDARIE";
DROP TABLE IF EXISTS "S01BOUNDARIE";
CREATE TABLE "S01BOUNDARIE" (
    -- UID interno GADM (único)
    nUidGadm INTEGER NOT NULL,
    
    -- Nivel 0 (País)
    cGid0 VARCHAR(5) NOT NULL,
    cName0 VARCHAR(100),
    cVarname0 VARCHAR(150),
    
    -- Nivel 1 (Regiones/Departamentos)
    cGid1 VARCHAR(20),
    cName1 VARCHAR(100),
    cVarname1 TEXT,
    cNlName1 VARCHAR(150),
    cIso1 VARCHAR(20),
    cHasc1 VARCHAR(20),
    cCc1 VARCHAR(20),
    cType1 VARCHAR(50),
    cEngtype1 VARCHAR(50),
    cValidfr1 VARCHAR(20),
    
    -- Nivel 2 (Provincias)
    cGid2 VARCHAR(20),
    cName2 VARCHAR(100),
    cVarname2 TEXT,
    cNlName2 VARCHAR(150),
    cHasc2 VARCHAR(20),
    cCc2 VARCHAR(20),
    cType2 VARCHAR(50),
    cEngtype2 VARCHAR(50),
    cValidfr2 VARCHAR(20),
    
    -- Nivel 3 (Distritos)
    cGid3 VARCHAR(20),
    cName3 VARCHAR(100),
    cVarname3 TEXT,
    cNlName3 VARCHAR(150),
    cHasc3 VARCHAR(20),
    cCc3 VARCHAR(20),
    cType3 VARCHAR(50),
    cEngtype3 VARCHAR(50),
    cValidfr3 VARCHAR(20),
    -- Nivel 4
    cGid4 VARCHAR(20),
    cName4 VARCHAR(100),
    cType4 VARCHAR(50),
    cEngtype4 VARCHAR(50),
    -- Nivel 5
    cGid5 VARCHAR(20),
    cName5 VARCHAR(100),
    cType5 VARCHAR(50),
    cEngtype5 VARCHAR(50),
    
    -- Contexto Geopolítico
    cSovereign VARCHAR(100),
    cGovernedby VARCHAR(100),
    cDisputedby TEXT,
    cRegion VARCHAR(100),
    cContinent VARCHAR(50),
    cCountry VARCHAR(100),
    
    -- Métricas
    nShapeLength DOUBLE PRECISION,
    nShapeArea DOUBLE PRECISION,
    
    -- Geometría
    gGeom GEOMETRY(MultiPolygon, 4326),
    
    -- PK compuesto único (código único por nivel jerárquico)
    CONSTRAINT pk_s01boundarie PRIMARY KEY (cGid0, cGid1, cGid2, cGid3, cGid4, cGid5)
);
-- Índices
CREATE INDEX idx_s01boundarie_name0 ON "S01BOUNDARIE"(cName0);
CREATE INDEX idx_s01boundarie_name1 ON "S01BOUNDARIE"(cName1);
CREATE INDEX idx_s01boundarie_name2 ON "S01BOUNDARIE"(cName2);
CREATE INDEX idx_s01boundarie_name3 ON "S01BOUNDARIE"(cName3);
CREATE INDEX idx_s01boundarie_country ON "S01BOUNDARIE"(cCountry);
CREATE INDEX idx_s01boundarie_uid ON "S01BOUNDARIE"(nUidGadm);
CREATE INDEX idx_s01boundarie_ggeom ON "S01BOUNDARIE" USING GIST (gGeom);

CREATE TABLE "S01VENUE_TYPE" (
	nIdVenueType SERIAL PRIMARY KEY,
	cName VARCHAR(100) NOT NULL,
	cDescription TEXT,
	bIsActive BOOLEAN DEFAULT TRUE
);

-- Como Venue o como Estudiante, empleado eetc
CREATE TABLE "S01CONTACT_ENTITY"(
	nIdContactEntity SERIAL PRIMARY KEY,
	cName VARCHAR(150) NOT NULL,
	cDescription TEXT,
	
	bIsActive BOOLEAN DEFAULT TRUE
);

--email, telefono etc
CREATE TABLE "S01CONTACT_TYPE"(
	nIdContactType SERIAL PRIMARY KEY,
	cName VARCHAR(150) NOT NULL,
	cDescription TEXT,
	
	bIsActive BOOLEAN DEFAULT TRUE
);

CREATE TABLE "S01CONTACT"(
	nIdContact BIGSERIAL PRIMARY KEY,
	nIdContactType INTEGER REFERENCES "S01CONTACT_TYPE"(nIdContactType),
	nIdContactEntity INTEGER REFERENCES "S01CONTACT_ENTITY"(nIdContactEntity),
	
	nIdEntity INTEGER,
	
	cValue VARCHAR(200),

	bIsActive BOOLEAN DEFAULT TRUE
);


CREATE TABLE "S01VENUE" (
    nIdVenue SERIAL PRIMARY KEY,
    nIdVenueType INTEGER  NOT NULL REFERENCES "S01VENUE_TYPE"(nIdVenueType),
    
    cName VARCHAR(100) NOT NULL,
    cDescription TEXT,
    cLogoUrl VARCHAR(500),
    
    -- Ubicación
    nUidGadm INTEGER NOT NULL REFERENCES "S01BOUNDARIE"(nUidGadm),
    cLocationDetail VARCHAR(300) NOT NULL,
    
    -- Geolocalización (VITAL para Google Maps)
    nLatitude DECIMAL(10, 8),
    nLongitude DECIMAL(11, 8),
    bIsActive BOOLEAN DEFAULT TRUE
);


CREATE TABLE "S01PROGRAM" (
	nIdProgram UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	nIdVenue INTEGER REFERENCES "S01VENUE"(nIdVenue),
	
	
	cName VARCHAR(150) NOT NULL,
	cDescription TEXT,
	
	
	cStatus VARCHAR(50) NOT NULL DEFAULT 'DRAFT'
        CHECK (cStatus IN ('DRAFT', 'SCHEDULED', 'ONGOING', 'CANCELLED')),
	cFlyer VARCHAR(500),
	
	tStartDate TIMESTAMP NOT NULL,
	tEndTime TIMESTAMP,
   
        
	bIsActive BOOLEAN DEFAULT TRUE 
);


CREATE TABLE "S01WORKSHOP" (
	nIdWorkshop UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	nIdProgram UUID REFERENCES "S01PROGRAM"(nIdProgram),
	
	cDescription TEXT,
	cStatus VARCHAR(50) NOT NULL DEFAULT 'DRAFT'
        CHECK (cStatus IN ('DRAFT', 'SCHEDULED', 'ONGOING', 'CANCELLED')),
	
	
	tDate TIMESTAMP NOT NULL,
		
	bIsActive BOOLEAN DEFAULT TRUE
);



CREATE TABLE "S01IDENTIFICATION_TYPE" (
    nIdIdentificationType SERIAL PRIMARY KEY,
    
    -- Código ISO 3166-1 alpha-2 (PE, CL, CO, etc.)
    cCountryIso CHAR(3) DEFAULT 'PE' NOT NULL, 
    
    -- El código de la entidad tributaria (SUNAT en Perú)
    cCode VARCHAR(5),  
    
    cName VARCHAR(100) NOT NULL,
    nMinLength INTEGER NOT NULL DEFAULT 1,
    nMaxLength INTEGER NOT NULL,
    bIsNumeric BOOLEAN DEFAULT TRUE,
    cRegex VARCHAR(100), -- Patrón de validación
    
    bIsActive BOOLEAN DEFAULT TRUE,
    
    -- La combinación PAÍS + CÓDIGO es lo que no se debe repetir
    CONSTRAINT uq_country_code UNIQUE(cCountryIso, cCode),
    -- El nombre también debe ser único por país
    CONSTRAINT uq_country_document_name UNIQUE(cCountryIso, cName)
);

CREATE OR REPLACE FUNCTION fn_validate_country_iso()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM "S01BOUNDARIE" WHERE cGid0 = NEW.cCountryIso LIMIT 1) THEN
        RAISE EXCEPTION 'El código de país % no existe en la tabla de fronteras', NEW.cCountryIso;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE TRIGGER tr_validate_country_before_insert
BEFORE INSERT OR UPDATE ON "S01IDENTIFICATION_TYPE"
FOR EACH ROW EXECUTE FUNCTION fn_validate_country_iso();

INSERT INTO "S01IDENTIFICATION_TYPE" (
    cCountryIso, 
    cCode, 
    cName, 
    nMinLength, 
    nMaxLength, 
    bIsNumeric, 
    cRegex
) VALUES (
    'PER',          -- ISO de 3 letras para coincidir con cGid0 de GADM
    '01',           -- Código SUNAT para DNI
    'DNI',          -- Nombre del documento
    8,              -- Longitud mínima
    8,              -- Longitud máxima
    TRUE,           -- Es numérico
    '^[0-9]{8}$'    -- El Regex: solo números, exactamente 8
);

SELECT * FROM "S01IDENTIFICATION_TYPE";

CREATE TABLE "S02PERSON" (
	nIdPerson UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	cName VARCHAR(100) NOT NULL,
	cLastName VARCHAR(100) NOT NULL,
	cBoundarie VARCHAR (150) REFERENCES
	nIdIdentificationType INTEGER NOT NULL REFERENCES "S01IDENTIFICATION_TYPE"(nIdIdentificationType),
	cIdentificationNumber VARCHAR(20) NOT NULL,

	tCreatedAt TIMESTAMP DEFAULT NOW(),
    tModifiedAt TIMESTAMP,
    
    CONSTRAINT uq_person_id UNIQUE(nIdIdentificationType, cIdentificationNumber)
);


CREATE TABLE "S02PARTICIPANT"(
	nIdParticipant UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	nIdPerson UUID REFERENCES "S02PERSON"(nIdPerson),
	
	jMetaData JSONB DEFAULT '{}'::JSONB,

	bIsActive BOOLEAN DEFAULT TRUE
);



CREATE TABLE "S02PARTICIPANT_PROGRAM"(	
	nIdParticipant UUID REFERENCES  "S02PARTICIPANT"(nIdParticipant),
	nIdProgram UUID REFERENCES "S01PROGRAM"(nIdProgram),
	
	bIsActive BOOLEAN DEFAULT TRUE,
	
	PRIMARY KEY (nIdParticipant, nIdProgram)
);




CREATE TABLE "S02USER"(
	nIdUser UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	cUsername VARCHAR (20) NOT NULL,
	cEmail VARCHAR(100) UNIQUE  NOT NULL,
	cHashedPassword VARCHAR(256) NOT NULL,
	cWallet VARCHAR(49) NOT NULL,
	
	tLatestAccess TIMESTAMP,
	CreatedAt TIMESTAMP DEFAULT NOW(),
	bIsActive BOOLEAN DEFAULT TRUE
);


CREATE TABLE "S02PERMISSION" (
	nIdPermission SERIAL PRIMARY KEY,
    cCode VARCHAR(50) NOT NULL UNIQUE,
    cName VARCHAR(100) NOT NULL,
    cDescription TEXT,
    cModule VARCHAR(50),
    bIsActive BOOLEAN DEFAULT TRUE,
    tCreatedAt TIMESTAMP DEFAULT NOW()
);

CREATE TABLE "S02ROLE" (
    nIdRole SERIAL PRIMARY KEY,
    
    cName VARCHAR(50) NOT NULL UNIQUE, 
    
    cDescription TEXT,
   
    bIsSystemRole BOOLEAN DEFAULT FALSE,
    
    bIsActive BOOLEAN DEFAULT TRUE,
    tCreatedAt TIMESTAMP DEFAULT NOW()
);


CREATE TABLE "S02ROLE_PERMISSION" (
    nIdRole INTEGER NOT NULL REFERENCES "S02ROLE"(nIdRole) ON DELETE CASCADE,
    nIdPermission INTEGER NOT NULL REFERENCES "S02PERMISSION"(nIdPermission) ON DELETE CASCADE,
    tCreatedAt TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (nIdRole, nIdPermission)
);

SELECT * FROM "S02ROLE_PERMISSION";

INSERT INTO "S02ROLE" (cName, cDescription, bIsSystemRole) VALUES
('GOD_MODE', 'Control total del sistema (SaaS Owner)', TRUE),
('EMPLOYEE', 'Administrador de la empresa organizadora', TRUE)
('EMPLOYEE', '')
('CUSTOMER')
('MAJOR')
ON CONFLICT (cName) DO NOTHING;



INSERT INTO "S02PERMISSION" (cCode, cName, cDescription, cModule, bIsActive) VALUES
-- Eventos
('CREATE_EVENT', 'Crear Evento', 'Permite crear nuevos eventos', 'EVENTS', TRUE),
('VIEW_EVENT', 'Ver Evento', 'Permite ver detalles de eventos', 'EVENTS', TRUE),
('EDIT_EVENT', 'Editar Evento', 'Permite editar eventos en estado DRAFT', 'EVENTS', TRUE),
('PUBLISH_EVENT', 'Publicar Evento', 'Permite publicar eventos', 'EVENTS', TRUE),
('DELETE_EVENT', 'Eliminar Evento', 'Permite eliminar/anular eventos', 'EVENTS', TRUE),
('CREATE_ACCESSTMP', 'Crear AccessTmp', 'Permite crear accesos temporales staff', 'EVENTS', TRUE),
('MANAGE_VENUES', 'Gestionar Locales', 'Crear y editar sedes de eventos', 'EVENTS', TRUE),
-- Tickets
('CREATE_TICKET', 'Crear Ticket', 'Permite crear nuevos tickets de evento', 'TICKETS', TRUE),
('VIEW_TICKET', 'Ver Ticket', 'Permite ver detalles de tickets', 'TICKETS', TRUE),
('EDIT_TICKET', 'Editar Ticket', 'Permite editar tickets en estado PENDING', 'TICKETS', TRUE),
('ISSUE_TICKET', 'Emitir Ticket', 'Permite emitir tickets', 'TICKETS', TRUE),
('CANCEL_TICKET', 'Cancelar Ticket', 'Permite cancelar tickets', 'TICKETS', TRUE),
-- Clientes y Pagos
('CREATE_CLIENT', 'Crear Cliente', 'Permite crear nuevos clientes', 'CLIENTS', TRUE),
('VIEW_CLIENT', 'Ver Cliente', 'Permite ver detalles de clientes', 'CLIENTS', TRUE),
('CREATE_PAYMENT', 'Crear Pago', 'Permite registrar nuevos pagos', 'PAYMENTS', TRUE),
('REFUND_PAYMENT', 'Revertir Pago', 'Permite revertir pagos (REFUND)', 'PAYMENTS', TRUE),
-- Operaciones y Admin
('SCAN_TICKET', 'Escanear Ticket', 'Permiso para validar entrada en puerta', 'OPERATIONS', TRUE),
('VIEW_DASHBOARD', 'Ver Dashboard', 'Ver estadísticas generales', 'REPORTS', TRUE),
('MANAGE_USERS', 'Gestionar Usuarios', 'Administración de cuentas', 'ADMIN', TRUE),
('SYSTEM_CONFIG', 'Configuración del Sistema', 'Acceso a config global', 'ADMIN', TRUE)
ON CONFLICT (cCode) DO NOTHING;


INSERT INTO "S02ROLE_PERMISSION"(nIdRole, nIdPermission)
SELECT r.nIdRole, p.nIdPermission 
FROM "S02ROLE" r, "S02PERMISSION" p 
WHERE r.cName = 'GOD_MODE'
ON CONFLICT DO NOTHING;



CREATE TABLE "S02EMPLOYEE" (
	nIdPerson UUID REFERENCES "S02PERSON"(nIdPerson) UNIQUE,
	nIdEmployee UUID REFERENCES "S02USER"(nIdUser),
	
	PRIMARY KEY (nIdEmployee),
	
	bIsActive BOOLEAN DEFAULT TRUE
);

CREATE TABLE "S02EMPLOYEE_PROGRAM"(
	nIdProgram UUID REFERENCES "S01PROGRAM"(nIdProgram),
	nIdEmployee UUID REFERENCES "S02EMPLOYEE"(nIdEmployee),
	
	PRIMARY KEY (nIdProgram, nIdEmployee)
);


--///////////////////////////////////////////////////////////////////////////////////////////

CREATE TABLE "S03METRIC_CATALOG"(
	nIdMetricCatalog SERIAL PRIMARY KEY 	
	
	cName VARCHAR (150) NOT NULL,
	cDescription TEXT,
	cDataType VARCHAR (100) NOT NULL,
	
	nIdQuestionnarie UUID REFERENCES "S03QUESTIONNARIE"(nIdQuestionnarie), --Puede ser null
	
	bIsActive BOOLEAN DEFAULT TRUE
);





