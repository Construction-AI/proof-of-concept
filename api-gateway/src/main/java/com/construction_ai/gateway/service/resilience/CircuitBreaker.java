package com.construction_ai.gateway.service.resilience;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class CircuitBreaker {
	private final Map<String, CircuitState> circuits = new ConcurrentHashMap<>();

	@Value("${gateway.circuit-breaker.failure-threshold}")
	private int failureThreshold;

	@Value("${gateway.circuit-breaker.reset-timeout-ms}")
	private long resetTimeoutMs;

	public boolean isAvailable(String serviceName) {
		CircuitState state = getOrCreateCircuit(serviceName);

		if (state.getState() == State.OPEN) {
			if (System.currentTimeMillis() - state.getLastStateChange() > resetTimeoutMs) {
				state.setState(State.HALF_OPEN);
			}
			else {
				return false;
			}
		}
		return true;
	}

	public void recordSuccess(String serviceName) {
		CircuitState state = getOrCreateCircuit(serviceName);
		state.recordSuccess();
	}
	
	public void recordFailure(String serviceName) {
		CircuitState state = getOrCreateCircuit(serviceName);
		state.recordFailure();
		
		if (state.getFailureCount() >= failureThreshold) {
			state.setState(State.OPEN);
		}
	}

	private CircuitState getOrCreateCircuit(String serviceName) {
        return circuits.computeIfAbsent(serviceName, k -> new CircuitState());
    }

	private class CircuitState {
		private State state = State.CLOSED;
		private int failureCount = 0;
		private long lastStateChange = System.currentTimeMillis();

		public int getFailureCount() {
			return this.failureCount;
		}

		public void setState(State newState) {
			this.state = newState;
			this.lastStateChange = System.currentTimeMillis();
		}

		public void recordFailure() {
			this.failureCount++;
		}

		public void recordSuccess() {
			this.failureCount = 0;
		}

		public State getState() {
			return this.state;
		}

		public long getLastStateChange() {
			return this.lastStateChange;
		}
	}

	private enum State {
        CLOSED, OPEN, HALF_OPEN
	}
}
