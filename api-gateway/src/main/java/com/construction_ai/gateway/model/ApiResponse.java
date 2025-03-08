package com.construction_ai.gateway.model;

import lombok.Data;

@Data
public class ApiResponse<T> {
	private boolean success;
	private T data;
	private String error, timestamp;

	public ApiResponse(boolean success, T data, String error, String timestamp) {
		this.success = success;
		this.data = data;
		this.error = error;
		this.timestamp = timestamp;
	}
}
