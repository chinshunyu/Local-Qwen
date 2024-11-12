package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "time"

    "github.com/google/uuid"
    "github.com/rs/cors"
)

type ChatRequest struct {
    BotType struct {
        Value string `json:"value"`
    } `json:"bot_type"`
    Messages       []interface{} `json:"messages"`
    MaxLength      int           `json:"max_length"`
    CurrentMessage struct {
        Role    string `json:"role"`
        Content string `json:"content"`
    } `json:"currentMessage"`
}

type ChatResponse struct {
    Response string `json:"response"`
    UserID   string `json:"user_id"`
}

// 生成ChatBot和SyntacticBot的响应
func generateChatResponse(userID string, messages []interface{}, maxLength int, currentMessage string, botType string) (string, error) {
    requestData := map[string]interface{}{
        "user_id":        userID,
        "messages":       messages,
        "max_length":     maxLength,
        "currentMessage": map[string]string{"role": "user", "content": currentMessage},
        "bot_type":       map[string]string{"value": botType},
    }

    // 将请求数据编码为JSON
    requestBody, err := json.Marshal(requestData)
    if err != nil {
        return "", fmt.Errorf("failed to marshal request data: %v", err)
    }

    // 发送请求到Python服务
    url := "http://127.0.0.1:5001/chat"
    req, err := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
    if err != nil {
        return "", fmt.Errorf("failed to create request: %v", err)
    }
    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return "", fmt.Errorf("failed to send request to Python server: %v", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return "", fmt.Errorf("received non-OK response from Python server: %d", resp.StatusCode)
    }

    // 读取响应数据
    var responseData map[string]interface{}
    if err := json.NewDecoder(resp.Body).Decode(&responseData); err != nil {
        return "", fmt.Errorf("failed to decode response data: %v", err)
    }

    responseText, ok := responseData["response"].(string)
    if !ok {
        return "", fmt.Errorf("response field missing or not a string")
    }

    return responseText, nil
}

func chatHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method == http.MethodOptions {
        // 处理预检请求
        w.Header().Set("Access-Control-Allow-Origin", r.Header.Get("Origin"))
        w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
        w.Header().Set("Access-Control-Allow-Credentials", "true")
        w.WriteHeader(http.StatusNoContent)
        return
    }

    var chatRequest ChatRequest
    if err := json.NewDecoder(r.Body).Decode(&chatRequest); err != nil {
        log.Printf("Failed to parse request body: %v", err)
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    botType := chatRequest.BotType.Value
    messages := chatRequest.Messages
    maxLength := chatRequest.MaxLength
    if maxLength == 0 {
        maxLength = 8000
    }
    currentMessage := chatRequest.CurrentMessage.Content

    userID, err := r.Cookie("user_id")
    if err != nil || userID.Value == "" {
        userID = &http.Cookie{
            Name:     "user_id",
            Value:    uuid.New().String(),
            HttpOnly: true,
            Secure:   true,
            SameSite: http.SameSiteNoneMode,
            Expires:  time.Now().Add(30 * 24 * time.Hour),
        }
        http.SetCookie(w, userID)
    }

    // 通道传递响应数据
    responseChan := make(chan ChatResponse)
    errorChan := make(chan error)

    // 启动 goroutine
    go func() {
        responseText, err := generateChatResponse(userID.Value, messages, maxLength, currentMessage, botType)
        if err != nil {
            errorChan <- err
            return
        }

        // 将生成的响应传递回主 goroutine
        responseChan <- ChatResponse{
            Response: responseText,
            UserID:   userID.Value,
        }
    }()

    select {
    case response := <-responseChan:
        // 设置响应头和CORS支持
        w.Header().Set("Content-Type", "application/json")
        w.Header().Set("Access-Control-Allow-Origin", r.Header.Get("Origin"))
        w.Header().Set("Access-Control-Allow-Credentials", "true")

        // 返回响应数据
        if err := json.NewEncoder(w).Encode(response); err != nil {
            log.Printf("Failed to encode response: %v", err)
            http.Error(w, "Failed to encode response", http.StatusInternalServerError)
        }
    case err := <-errorChan:
        log.Printf("Failed to generate chat response: %v", err)
        http.Error(w, "Failed to generate chat response", http.StatusInternalServerError)
    case <-time.After(60 * time.Second): // 超时处理
        log.Printf("Chat response generation timed out")
        http.Error(w, "Chat response generation timed out", http.StatusGatewayTimeout)
    }
}

func main() {
    // 设置CORS
    corsHandler := cors.New(cors.Options{
        AllowedOrigins:   []string{"https://c903-139-227-188-50.ngrok-free.app", "http://127.0.0.1:9100"},
        AllowCredentials: true,
        AllowedMethods:   []string{"POST", "OPTIONS"},
        AllowedHeaders:   []string{"Content-Type"},
    })

    http.HandleFunc("/chat", chatHandler)

    // 启动HTTP服务器
    server := &http.Server{
        Addr:    ":5002",
        Handler: corsHandler.Handler(http.DefaultServeMux),
    }

    log.Println("Starting server on port 5002...")
    if err := server.ListenAndServe(); err != nil {
        log.Fatalf("Failed to start server: %v", err)
    }
}


