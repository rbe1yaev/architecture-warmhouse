package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"strings"
	"time"
)

type Response struct {
	Location    string    `json:"location,omitempty"`
	SensorID    string    `json:"sensor_id,omitempty"`
	Temperature float64   `json:"temperature"`
	Unit        string    `json:"unit"`
	Timestamp   time.Time `json:"timestamp"`
}

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

func randomTemp() (float64, string) {
	temp := 10 + rand.Float64()*25

	var status string

	if temp < 20 {
		status = "Cold"
	} else if temp < 25 {
		status = "Normal"
	} else {
		status = "Hell"
	}

	return temp, status
}

func writeJSON(w http.ResponseWriter, data any) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(data)
}

func temperatureByLocation(w http.ResponseWriter, r *http.Request) {
	location := r.URL.Query().Get("location")
	if location == "" {
		location = "Unknown"
	}
	sensorID := "0"

	switch location {
	case "Living Room":
		sensorID = "1"
	case "Bedroom":
		sensorID = "2"
	case "Kitchen":
		sensorID = "3"
	}

	temp, status := randomTemp()

	resp := TemperatureResponse{
		Value:       temp,
		Unit:        "C",
		Timestamp:   time.Now().UTC(),
		Location:    location,
		Status:      status,
		SensorID:    sensorID,
		SensorType:  "smart",
		Description: fmt.Sprintf("The sensor in %s", location),
	}

	writeJSON(w, resp)
}

func temperatureByID(w http.ResponseWriter, r *http.Request) {
	sensorID := strings.TrimPrefix(r.URL.Path, "/temperature/")

	if sensorID == "" || sensorID == "temperature" {
		http.Error(w, "missing id", http.StatusBadRequest)
		return
	}
	var location string

	switch sensorID {
	case "1":
		location = "Living Room"
	case "2":
		location = "Bedroom"
	case "3":
		location = "Kitchen"
	default:
		location = "Unknown"
	}

	temp, status := randomTemp()

	resp := TemperatureResponse{
		Value:       temp,
		Unit:        "C",
		Timestamp:   time.Now().UTC(),
		Location:    location,
		Status:      status,
		SensorID:    sensorID,
		SensorType:  "smart",
		Description: fmt.Sprintf("The sensor in %s", location),
	}

	writeJSON(w, resp)
}

func main() {
	rand.Seed(time.Now().UnixNano())

	mux := http.NewServeMux()

	mux.HandleFunc("/temperature", temperatureByLocation)
	mux.HandleFunc("/temperature/", temperatureByID)

	server := &http.Server{
		Addr:         ":8081",
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
		Handler:      mux,
	}

	println("temperature-api running on :8081")
	_ = server.ListenAndServe()
}
