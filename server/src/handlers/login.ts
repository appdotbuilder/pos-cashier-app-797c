
import { type LoginInput, type LoginResponse } from '../schema';

export async function login(input: LoginInput): Promise<LoginResponse> {
    // This is a placeholder declaration! Real code should be implemented here.
    // The goal of this handler is to authenticate a user with username and password.
    // For now, we'll check against a demo user (username: "demo", password: "demo123")
    
    const DEMO_USERNAME = "demo";
    const DEMO_PASSWORD = "demo123";
    
    if (input.username === DEMO_USERNAME && input.password === DEMO_PASSWORD) {
        return {
            success: true,
            message: "Login successful",
            user: {
                id: 1,
                username: DEMO_USERNAME
            }
        };
    }
    
    return {
        success: false,
        message: "Invalid username or password"
    };
}
