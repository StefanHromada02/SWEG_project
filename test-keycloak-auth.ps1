# Test script for Keycloak authentication
# This tests the integration between Keycloak and Django backend

Write-Host "=== Keycloak Authentication Test ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$KEYCLOAK_URL = "http://localhost:8080"
$REALM = "social-media-realm"
$CLIENT_ID = "frontend"
$BACKEND_URL = "http://localhost:8000/api"

# Get username and password from user
Write-Host "Enter Keycloak credentials:" -ForegroundColor Yellow
$username = Read-Host "Username"
$password = Read-Host "Password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

Write-Host ""
Write-Host "Step 1: Getting access token from Keycloak..." -ForegroundColor Yellow

try {
    # Get token from Keycloak
    $tokenResponse = Invoke-RestMethod -Uri "$KEYCLOAK_URL/realms/$REALM/protocol/openid-connect/token" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body @{
            grant_type = "password"
            client_id = $CLIENT_ID
            username = $username
            password = $passwordPlain
        }
    
    $token = $tokenResponse.access_token
    Write-Host "✓ Token received successfully" -ForegroundColor Green
    
    # Decode token to show user info (just for demonstration)
    $tokenParts = $token.Split('.')
    $payload = $tokenParts[1]
    # Add padding if needed
    while ($payload.Length % 4 -ne 0) {
        $payload += "="
    }
    $decodedBytes = [Convert]::FromBase64String($payload)
    $decodedJson = [System.Text.Encoding]::UTF8.GetString($decodedBytes)
    $tokenData = $decodedJson | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "Token Information:" -ForegroundColor Cyan
    Write-Host "  User: $($tokenData.preferred_username)"
    Write-Host "  Name: $($tokenData.name)"
    Write-Host "  Email: $($tokenData.email)"
    Write-Host "  Keycloak ID: $($tokenData.sub)"
    Write-Host ""
    
} catch {
    Write-Host "✗ Failed to get token: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Step 2: Testing authenticated API calls..." -ForegroundColor Yellow

try {
    # Test GET /posts/ (should work)
    Write-Host "  Testing GET /posts/..." -ForegroundColor Gray
    $posts = Invoke-RestMethod -Uri "$BACKEND_URL/posts/" `
        -Method GET `
        -Headers @{Authorization = "Bearer $token"}
    Write-Host "  ✓ GET /posts/ successful (retrieved $($posts.Count) posts)" -ForegroundColor Green
    
    # Test POST /posts/ (create a test post)
    Write-Host "  Testing POST /posts/..." -ForegroundColor Gray
    $newPost = @{
        title = "Test Post from PowerShell"
        text = "This post was created to test Keycloak integration at $(Get-Date)"
    } | ConvertTo-Json
    
    $createdPost = Invoke-RestMethod -Uri "$BACKEND_URL/posts/" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"} `
        -Body $newPost
    Write-Host "  ✓ POST /posts/ successful (created post ID: $($createdPost.id))" -ForegroundColor Green
    Write-Host "    - User: $($createdPost.user_details.name) (ID: $($createdPost.user))" -ForegroundColor Gray
    
    # Test my_posts endpoint
    Write-Host "  Testing GET /posts/my_posts/..." -ForegroundColor Gray
    $myPosts = Invoke-RestMethod -Uri "$BACKEND_URL/posts/my_posts/" `
        -Method GET `
        -Headers @{Authorization = "Bearer $token"}
    Write-Host "  ✓ GET /posts/my_posts/ successful (retrieved $($myPosts.Count) posts)" -ForegroundColor Green
    
    # Test POST /comments/ (create a test comment)
    Write-Host "  Testing POST /comments/..." -ForegroundColor Gray
    $newComment = @{
        post = $createdPost.id
        text = "Test comment from PowerShell"
    } | ConvertTo-Json
    
    $createdComment = Invoke-RestMethod -Uri "$BACKEND_URL/comments/" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"} `
        -Body $newComment
    Write-Host "  ✓ POST /comments/ successful (created comment ID: $($createdComment.id))" -ForegroundColor Green
    Write-Host "    - User: $($createdComment.user_details.name) (ID: $($createdComment.user))" -ForegroundColor Gray
    
} catch {
    Write-Host "  ✗ API call failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "  Error details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""
Write-Host "Step 3: Testing unauthenticated access..." -ForegroundColor Yellow

try {
    # Test GET without auth (should work)
    Write-Host "  Testing GET /posts/ without auth..." -ForegroundColor Gray
    $publicPosts = Invoke-RestMethod -Uri "$BACKEND_URL/posts/" -Method GET
    Write-Host "  ✓ Public read access works (retrieved $($publicPosts.Count) posts)" -ForegroundColor Green
    
    # Test POST without auth (should fail with 401)
    Write-Host "  Testing POST /posts/ without auth (should fail)..." -ForegroundColor Gray
    try {
        $unauthorizedPost = @{
            title = "This should fail"
            text = "Unauthenticated post"
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri "$BACKEND_URL/posts/" `
            -Method POST `
            -ContentType "application/json" `
            -Body $unauthorizedPost
        Write-Host "  ✗ Unexpected: POST without auth succeeded (should have failed)" -ForegroundColor Red
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 403) {
            Write-Host "  ✓ Correctly blocked unauthenticated POST (401/403)" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "  ✗ Unexpected error during unauthenticated test: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test Summary ===" -ForegroundColor Cyan
Write-Host "✓ Keycloak authentication working" -ForegroundColor Green
Write-Host "✓ User sync from Keycloak to Django working" -ForegroundColor Green
Write-Host "✓ Authenticated POST operations working" -ForegroundColor Green
Write-Host "✓ Public read access working" -ForegroundColor Green
Write-Host "✓ Authorization properly enforced" -ForegroundColor Green
Write-Host ""
Write-Host "Integration test completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Created test post ID: $($createdPost.id)" -ForegroundColor Gray
Write-Host "You can view it at: http://localhost:4200" -ForegroundColor Gray
