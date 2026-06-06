package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"time"
)

// TemperatureResponse represents the response from the temperature API.
// Fields match the structure expected by smart_home TemperatureService.
type TemperatureResponse struct {
	Value       float64   `json:"value"`
	Unit        string    `json:"unit"`
	Timestamp   time.Time `json:"timestamp"`
	Location    string    `json:"location"`
	Status      string    `json:"status"`
	SensorID    string    `json:"sensor_id"`
	SensorType  string    `json:"sensor_type"`
	Description string    `json:"description"`
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/temperature", handleTemperature)
	mux.HandleFunc("/temperature/", handleTemperatureByID) // GET /temperature/{id}
	mux.HandleFunc("/health", handleHealth)

	port := getEnv("PORT", "8081")
	addr := fmt.Sprintf(":%s", port)
	log.Printf("temperature-api starting on %s", addr)

	server := &http.Server{
		Addr:         addr,
		Handler:      mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("server error: %v", err)
	}
}

func handleTemperature(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	location := r.URL.Query().Get("location")
	if location == "" {
		location = "unknown"
	}

	// Random temperature in range [-10, 40] celsius, rounded to 2 decimal places
	value := -10.0 + rand.Float64()*50.0
	value = math.Round(value*100) / 100

	resp := TemperatureResponse{
		Value:       value,
		Unit:        "celsius",
		Timestamp:   time.Now().UTC(),
		Location:    location,
		Status:      "ok",
		SensorID:    fmt.Sprintf("temp-%s-%d", location, time.Now().UnixNano()),
		SensorType:  "temperature",
		Description: "Temperature sensor reading",
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		log.Printf("encode error: %v", err)
	}
}

// handleTemperatureByID handles GET /temperature/{id}
// smart_home calls this as /temperature/<sensor_id> (numeric)
func handleTemperatureByID(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Extract id from path: /temperature/<id>
	sensorID := r.URL.Path[len("/temperature/"):]
	if sensorID == "" {
		http.Error(w, "sensor id required", http.StatusBadRequest)
		return
	}

	value := -10.0 + rand.Float64()*50.0
	value = math.Round(value*100) / 100

	resp := TemperatureResponse{
		Value:       value,
		Unit:        "celsius",
		Timestamp:   time.Now().UTC(),
		Location:    fmt.Sprintf("sensor-%s", sensorID),
		Status:      "ok",
		SensorID:    sensorID,
		SensorType:  "temperature",
		Description: "Temperature sensor reading",
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		log.Printf("encode error: %v", err)
	}
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprint(w, `{"status":"ok"}`)
}

func getEnv(key, defaultValue string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultValue
}
