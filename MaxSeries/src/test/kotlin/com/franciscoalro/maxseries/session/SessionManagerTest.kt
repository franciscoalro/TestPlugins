package com.franciscoalro.maxseries.session

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Testes para SessionManager
 * 
 * Nota: Estes testes requerem Robolectric para mockar o Android Context
 * e SharedPreferences.
 */
@RunWith(RobolectricTestRunner::class)
@Config(manifest = Config.NONE)
class SessionManagerTest {
    
    private lateinit var context: Context
    private lateinit var sessionManager: SessionManager
    
    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()
        sessionManager = SessionManager(context, defaultTTLMinutes = 5)
    }
    
    @Test
    fun `test session data validity`() {
        val validSession = SessionManager.SessionData(
            domain = "test.com",
            cookies = mapOf("session" to "abc123"),
            tokens = emptyMap(),
            headers = emptyMap(),
            timestamp = System.currentTimeMillis(),
            ttlMinutes = 5
        )
        
        assert(validSession.isValid())
        assert(validSession.remainingMinutes() > 0)
    }
    
    @Test
    fun `test expired session`() {
        val expiredSession = SessionManager.SessionData(
            domain = "test.com",
            cookies = emptyMap(),
            tokens = emptyMap(),
            headers = emptyMap(),
            timestamp = System.currentTimeMillis() - (10 * 60 * 1000), // 10 minutos atrás
            ttlMinutes = 5
        )
        
        assert(!expiredSession.isValid())
        assert(expiredSession.remainingMinutes() == 0)
    }
    
    @Test
    fun `test session metadata`() {
        val metadata = SessionManager.SessionMetadata(
            playerType = SessionManager.SessionMetadata.PlayerType.PLAYEREMBEDAPI,
            videoId = "12345",
            slug = "abc123"
        )
        
        assert(metadata.playerType == SessionManager.SessionMetadata.PlayerType.PLAYEREMBEDAPI)
        assert(metadata.videoId == "12345")
        assert(metadata.slug == "abc123")
    }
    
    @Test
    fun `test session metrics`() {
        val metrics = SessionManager.SessionMetrics(
            cacheHits = 10,
            cacheMisses = 5,
            renewals = 2,
            creations = 3
        )
        
        assert(metrics.cacheHits == 10)
        assert(metrics.cacheMisses == 5)
        assert(metrics.hitRate() == 10f / 15f)
    }
    
    @Test
    fun `test bypass headers`() {
        val headers = SessionManager.BYPASS_HEADERS
        
        assert(headers.containsKey("X-Requested-With"))
        assert(headers.containsKey("Accept"))
        assert(headers["X-Requested-With"] == "XMLHttpRequest")
    }
    
    @Test
    fun `test user agents`() {
        val userAgents = SessionManager.USER_AGENTS
        
        assert(userAgents.isNotEmpty())
        assert(userAgents.all { it.contains("Mozilla") })
    }
    
    @Test
    fun `test clear all sessions`() {
        sessionManager.clearAllSessions()
        
        val metrics = sessionManager.getMetrics()
        // Após limpar, não deve haver sessões
    }
}

/**
 * Testes simples que não requerem Android Context
 */
class SessionManagerSimpleTest {
    
    @Test
    fun `test session data structure`() {
        val session = SessionManager.SessionData(
            domain = "playerembedapi.link",
            cookies = mapOf("csrf" to "token123"),
            tokens = mapOf("api_key" to "secret"),
            headers = mapOf("Referer" to "https://example.com"),
            ttlMinutes = 30
        )
        
        assert(session.domain == "playerembedapi.link")
        assert(session.cookies["csrf"] == "token123")
        assert(session.tokens["api_key"] == "secret")
        assert(session.ttlMinutes == 30)
    }
    
    @Test
    fun `test player type enum`() {
        val types = SessionManager.SessionMetadata.PlayerType.values()
        
        assert(types.contains(SessionManager.SessionMetadata.PlayerType.PLAYEREMBEDAPI))
        assert(types.contains(SessionManager.SessionMetadata.PlayerType.MEGAEMBED))
        assert(types.contains(SessionManager.SessionMetadata.PlayerType.UNKNOWN))
    }
}
