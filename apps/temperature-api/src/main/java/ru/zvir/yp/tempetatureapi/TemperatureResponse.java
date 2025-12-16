package ru.zvir.yp.tempetatureapi;

public class TemperatureResponse {
    float value;
    String unit;
    String timestamp;
    String location;
    String status;
    String sensor_id;
    String sensor_type;
    String description;


    public TemperatureResponse() {
    }

    public TemperatureResponse(float value, String unit, String timestamp, String location, String status, String sensor_id, String sensor_type, String description) {
        this.value = value;
        this.unit = unit;
        this.timestamp = timestamp;
        this.location = location;
        this.status = status;
        this.sensor_id = sensor_id;
        this.sensor_type = sensor_type;
        this.description = description;
    }

    public float getValue() {
        return value;
    }

    public void setValue(float value) {
        this.value = value;
    }

    public String getUnit() {
        return unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getSensor_id() {
        return sensor_id;
    }

    public void setSensor_id(String sensor_id) {
        this.sensor_id = sensor_id;
    }

    public String getSensor_type() {
        return sensor_type;
    }

    public void setSensor_type(String sensor_type) {
        this.sensor_type = sensor_type;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
