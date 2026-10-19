package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

// ==========================================
// 1. Estructuras para leer el archivo de TinyDB
// ==========================================
type TinyDBRoot struct {
	Default map[string]RawStation `json:"_default"`
}

type RawStation struct {
	ID          int          `json:"ID"`
	AddressInfo Address      `json:"AddressInfo"`
	Connections []Connection `json:"Connections"`
}

type Address struct {
	Title     string  `json:"Title"`
	Latitude  float64 `json:"Latitude"`
	Longitude float64 `json:"Longitude"`
	Town      string  `json:"Town"`
}

type Connection struct {
	ConnectionType struct {
		Title string `json:"Title"`
	} `json:"ConnectionType"`
	PowerKW float64 `json:"PowerKW"`
}

// ==========================================
// 2. Estructuras de salida (Spatial ETL & Normalización)
// ==========================================
type GeoJSONPoint struct {
	Type        string    `json:"type"`        // "Point"
	Coordinates []float64 `json:"coordinates"` // [Longitud, Latitud] para estándares geoespaciales
}

type NormalizedStation struct {
	ID                 string       `json:"id"`
	Name               string       `json:"name"`
	City               string       `json:"city"`
	StandardizedConns  []string     `json:"standardized_connectors"`
	MaxPowerKW         float64      `json:"max_power_kw"`
	Geometry           GeoJSONPoint `json:"geometry"` // Entidad geométrica vectorial
}

// ==========================================
// 3. Funciones de Limpieza y Estandarización
// ==========================================
func normalizeConnector(rawTitle string) string {
	title := strings.ToLower(rawTitle)
	
	// Estandarización de nomenclaturas heterogéneas
	if strings.Contains(title, "type 2") || strings.Contains(title, "mennekes") {
		return "IEC_62196_Type_2"
	} else if strings.Contains(title, "ccs") || strings.Contains(title, "combo") {
		return "CCS_Combo"
	} else if strings.Contains(title, "chademo") {
		return "CHAdeMO"
	} else if strings.Contains(title, "j1772") {
		return "SAE_J1772"
	} else if strings.Contains(title, "tesla") {
		return "Tesla_Supercharger"
	}
	return "Unknown_Connector"
}

// ==========================================
// 4. Proceso Principal (Pipeline ETL)
// ==========================================
func main() {
	// Paso 1: Leer el archivo de la TinyDB generada previamente (ej. db.json)
	file, err := os.Open("db.json")
	if err != nil {
		fmt.Printf("Error al abrir la base de datos TinyDB: %v\n", err)
		return
	}
	defer file.Close()

	var db TinyDBRoot
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&db); err != nil {
		fmt.Printf("Error al decodificar el esquema JSON: %v\n", err)
		return
	}

	var processedStations []NormalizedStation

	// Paso 2: Limpieza, Normalización y Spatial ETL
	for _, raw := range db.Default {
		var cleanConns []string
		maxPower := 0.0

		// Estandarización de campos anidados (conectores y potencias)
		for _, conn := range raw.Connections {
			stdName := normalizeConnector(conn.ConnectionType.Title)
			cleanConns = append(cleanConns, stdName)
			
			if conn.PowerKW > maxPower {
				maxPower = conn.PowerKW
			}
		}

		// Paso 3: Spatial ETL (Transformación tabular a Entidad Vectorial GeoJSON)
		// Nota: GeoJSON almacena las coordenadas estrictamente en formato [Longitud, Latitud]
		geometryVectorial := GeoJSONPoint{
			Type:        "Point",
			Coordinates: []float64{raw.AddressInfo.Longitude, raw.AddressInfo.Latitude},
		}

		// Construcción de la entidad normalizada y enriquecida
		station := NormalizedStation{
			ID:                fmt.Sprintf("station_%d", raw.ID),
			Name:              raw.AddressInfo.Title,
			City:              raw.AddressInfo.Town,
			StandardizedConns: cleanConns,
			MaxPowerKW:        maxPower,
			Geometry:          geometryVectorial,
		}

		processedStations = append(processedStations, station)
	}

	// Paso 4: Exportación de datos listos para análisis espacial o Sistemas de Información Geográfica (GIS)
	outputData, err := json.MarshalIndent(processedStations, "", "  ")
	if err != nil {
		fmt.Printf("Error al serializar los datos procesados: %v\n", err)
		return
	}

	err = os.WriteFile("spatial_etl_output.json", outputData, 0644)
	if err != nil {
		fmt.Printf("Error al guardar el archivo de salida: %v\n", err)
		return
	}

	fmt.Printf("Spatial ETL completado exitosamente. %d estaciones procesadas, normalizadas y convertidas a geometría vectorial en 'spatial_etl_output.json'.\n", len(processedStations))
}