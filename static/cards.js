// /static/cards.js - COMPLETE FIXED VERSION
// /static/cards.js - ADD THIS AT THE VERY TOP

// ===== MOBILE DETECTION & OPTIMIZATION =====
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const isTablet = /iPad|Android(?!.*Mobile)|Tablet|Silk/i.test(navigator.userAgent);

// Performance optimization flags
const PERFORMANCE_OPTIMIZATIONS = {
    isMobile: isMobile || isTablet,
    reduceAnimations: isMobile || isTablet,
    simplifyGraphics: isMobile,
    reduceParticles: isMobile,
    useLowerQuality: isMobile
};

console.log(`📱 Device: ${isMobile ? 'Mobile' : isTablet ? 'Tablet' : 'Desktop'} - Optimizations: ${PERFORMANCE_OPTIMIZATIONS.reduceAnimations ? 'ON' : 'OFF'}`);

// Apply optimizations immediately
if (PERFORMANCE_OPTIMIZATIONS.reduceAnimations) {
    // These will override the ANIMATIONS constants below
    window.MOBILE_ANIMATION_SETTINGS = {
        hover: {
            lift: 4,           // Reduced from 8
            scale: 1.03,       // Reduced from 1.05
            shadowBlur: 8,     // Reduced from 15
            duration: 100      // Reduced from 150
        },
        play: {
            duration: 400,     // Reduced from 800
            easing: 'ease-out' // Simpler easing
        },
        threeSpades: {
            glowBlur: 10,      // Reduced from 20
            pulseDuration: 1000 // Reduced from 2000
        },
        autoWinCard: {
            glowBlur: 15,      // Reduced from 25
            pulseDuration: 800 // Reduced from 1500
        }
    };
}
// ===== END MOBILE OPTIMIZATION =====
const cardRenderer = {
    // Animation constants
    ANIMATIONS: {
        hover: {
            lift: 8,
            scale: 1.05,
            shadow: 'rgba(78, 205, 196, 0.5)',
            shadowBlur: 15,
            duration: 150
        },
        play: {
            duration: 800,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
        },
        threeSpades: {
            glowColor: 'rgba(0, 255, 0, 0.7)',
            glowBlur: 20,
            pulseDuration: 2000
        },
        autoWinCard: {
            glowColor: 'rgba(255, 215, 0, 0.7)',
            glowBlur: 25,
            pulseDuration: 1500
        }
    },
    
    // Game state for highlighting rules
    gameState: {
        isFirstRound: false,
        requiresThreeSpades: false,
        threeSpadesPlayer: null,
        currentPlayerIndex: 0,
        firstPlayerIndex: 0,
        roundNumber: 1,
        autoWinner: null
    },
    
    // Update game state for rule highlighting
    updateGameState: function(state) {
        if (state) {
            this.gameState.isFirstRound = (state.round_number === 1);
            this.gameState.requiresThreeSpades = state.rules_info ? state.rules_info.requires_three_spades : false;
            this.gameState.threeSpadesPlayer = state.rules_info ? state.rules_info.three_spades_player : null;
            this.gameState.currentPlayerIndex = state.current_player_index || 0;
            this.gameState.firstPlayerIndex = state.first_player_index || 0;
            this.gameState.roundNumber = state.round_number || 1;
            this.gameState.autoWinner = state.auto_winner || null;
        }
    },
    
    // Convert rank number to display symbol
    rankToSymbol: function(rank) {
        if (rank === 11) return 'J';
        if (rank === 12) return 'Q';
        if (rank === 13) return 'K';
        if (rank === 14) return 'A';
        if (rank === 2) return '2';
        return rank.toString();
    },
    
    // Check if card is 3♠
    isThreeOfSpades: function(card) {
        return card && card.rank === 3 && card.suit === '♠';
    },
    
    // Check if card should be highlighted as 3♠
    shouldHighlightThreeSpades: function(card, isPlayerCard = true) {
        // Only highlight 3♠ in player's hand during first round when required
        if (!this.isThreeOfSpades(card)) return false;
        
        if (isPlayerCard) {
            // Player's card - highlight if it's first round and requires 3♠
            return this.gameState.isFirstRound && 
                   this.gameState.requiresThreeSpades && 
                   this.gameState.currentPlayerIndex === 0;
        } else {
            // Bot's card or table card - always highlight 3♠
            return true;
        }
    },
    
    // Draw a single card face with enhanced hover effects and highlighting
    drawCardFace: function(ctx, card, x, y, isSelected = false, isHovered = false, isAnimating = false, isPlayerCard = true) {
        // Use bigger size for player cards, normal for others
        const baseWidth = isPlayerCard ? 72 : 60;
        const baseHeight = isPlayerCard ? 101 : 84;
        
        // Apply hover effect
        let width = baseWidth;
        let height = baseHeight;
        let hoverOffsetY = 0;
        let shadowEffect = null;
        let borderGlow = false;
        
        if (isHovered && !isSelected && !isAnimating) {
            // Hover effect: slight lift and scale
            hoverOffsetY = -this.ANIMATIONS.hover.lift;
            width = baseWidth * this.ANIMATIONS.hover.scale;
            height = baseHeight * this.ANIMATIONS.hover.scale;
            shadowEffect = {
                color: this.ANIMATIONS.hover.shadow,
                blur: this.ANIMATIONS.hover.shadowBlur,
                offsetX: 0,
                offsetY: this.ANIMATIONS.hover.lift
            };
            borderGlow = true;
        }
        
        const borderRadius = isPlayerCard ? 10 : 8;
        const textOffset = isPlayerCard ? 10 : 8;
        
        // Adjust position for centered scaling
        const adjustedX = x - (width - baseWidth) / 2;
        const adjustedY = y + hoverOffsetY - (height - baseHeight) / 2;
        
        // Save context
        ctx.save();
        
        // Apply selection lift (more than hover)
        const selectionLift = isPlayerCard ? 18 : 15;
        const finalY = isSelected ? adjustedY - selectionLift : adjustedY;
        
        // Check if this is 3♠ that needs highlighting
        const isThreeSpades = this.isThreeOfSpades(card);
        const highlightThreeSpades = this.shouldHighlightThreeSpades(card, isPlayerCard);
        
        // Special highlighting for automatic win cards
        const isSpecialCard = (card.rank === 2) || (card.rank === 3 && this.gameState.roundNumber === 1);
        
        // Apply shadow if hovering or if it's a highlighted card
        if (shadowEffect) {
            ctx.shadowColor = shadowEffect.color;
            ctx.shadowBlur = shadowEffect.blur;
            ctx.shadowOffsetX = shadowEffect.offsetX;
            ctx.shadowOffsetY = shadowEffect.offsetY;
        } else if (highlightThreeSpades && !isAnimating) {
            // Special glow for 3♠
            const pulse = (Date.now() % this.ANIMATIONS.threeSpades.pulseDuration) / this.ANIMATIONS.threeSpades.pulseDuration;
            const glowIntensity = 0.5 + 0.5 * Math.sin(pulse * Math.PI * 2);
            ctx.shadowColor = `rgba(0, 255, 0, ${0.3 + glowIntensity * 0.4})`;
            ctx.shadowBlur = 15 + glowIntensity * 10;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 0;
        } else if (isSpecialCard && isPlayerCard && !isAnimating) {
            // Special glow for 2s and 3s (automatic win cards)
            const pulse = (Date.now() % this.ANIMATIONS.autoWinCard.pulseDuration) / this.ANIMATIONS.autoWinCard.pulseDuration;
            const glowIntensity = 0.5 + 0.5 * Math.sin(pulse * Math.PI * 2);
            const color = card.rank === 2 ? '255, 215, 0' : '0, 255, 0'; // Gold for 2s, Green for 3s
            ctx.shadowColor = `rgba(${color}, ${0.3 + glowIntensity * 0.4})`;
            ctx.shadowBlur = 20 + glowIntensity * 10;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 0;
        }
        
        // Draw card background with rounded corners
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        if (ctx.roundRect) {
            ctx.roundRect(adjustedX, finalY, width, height, borderRadius);
        } else {
            // Fallback for browsers without roundRect
            ctx.moveTo(adjustedX + borderRadius, finalY);
            ctx.lineTo(adjustedX + width - borderRadius, finalY);
            ctx.quadraticCurveTo(adjustedX + width, finalY, adjustedX + width, finalY + borderRadius);
            ctx.lineTo(adjustedX + width, finalY + height - borderRadius);
            ctx.quadraticCurveTo(adjustedX + width, finalY + height, adjustedX + width - borderRadius, finalY + height);
            ctx.lineTo(adjustedX + borderRadius, finalY + height);
            ctx.quadraticCurveTo(adjustedX, finalY + height, adjustedX, finalY + height - borderRadius);
            ctx.lineTo(adjustedX, finalY + borderRadius);
            ctx.quadraticCurveTo(adjustedX, finalY, adjustedX + borderRadius, finalY);
        }
        ctx.closePath();
        ctx.fill();
        
        // Clear shadow for border drawing
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        
        // Card border with special effects
        let borderColor = '#CCCCCC';
        let borderWidth = 1;
        
        if (isSelected) {
            borderColor = '#FFD700';
            borderWidth = 3;
            
            // Add glow to selected cards
            if (borderGlow) {
                ctx.shadowColor = 'rgba(255, 215, 0, 0.6)';
                ctx.shadowBlur = 10;
            }
        } else if (isHovered) {
            borderColor = '#4ECDC4';
            borderWidth = 2;
            
            // Add glow to hovered cards
            if (borderGlow) {
                ctx.shadowColor = 'rgba(78, 205, 196, 0.5)';
                ctx.shadowBlur = 8;
            }
        } else if (highlightThreeSpades) {
            // Special border for 3♠
            borderColor = '#00FF00';
            borderWidth = 3;
            
            // Add green glow for 3♠
            const pulse = (Date.now() % this.ANIMATIONS.threeSpades.pulseDuration) / this.ANIMATIONS.threeSpades.pulseDuration;
            const glowIntensity = 0.5 + 0.5 * Math.sin(pulse * Math.PI * 2);
            ctx.shadowColor = `rgba(0, 255, 0, ${0.4 + glowIntensity * 0.3})`;
            ctx.shadowBlur = 10 + glowIntensity * 5;
        } else if (isSpecialCard && isPlayerCard) {
            // Special border for 2s and 3s (automatic win cards)
            borderColor = card.rank === 2 ? '#FFD700' : '#00FF00';
            borderWidth = 3;
            
            const pulse = (Date.now() % this.ANIMATIONS.autoWinCard.pulseDuration) / this.ANIMATIONS.autoWinCard.pulseDuration;
            const glowIntensity = 0.5 + 0.5 * Math.sin(pulse * Math.PI * 2);
            const color = card.rank === 2 ? '255, 215, 0' : '0, 255, 0';
            ctx.shadowColor = `rgba(${color}, ${0.4 + glowIntensity * 0.3})`;
            ctx.shadowBlur = 15 + glowIntensity * 8;
        }
        
        // Draw border
        ctx.strokeStyle = borderColor;
        ctx.lineWidth = borderWidth;
        ctx.stroke();
        
        // Clear shadow again for content
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        
        // Clip the drawing area to prevent text from overflowing
        ctx.save();
        ctx.beginPath();
        if (ctx.roundRect) {
            ctx.roundRect(adjustedX, finalY, width, height, borderRadius);
        } else {
            ctx.moveTo(adjustedX + borderRadius, finalY);
            ctx.lineTo(adjustedX + width - borderRadius, finalY);
            ctx.quadraticCurveTo(adjustedX + width, finalY, adjustedX + width, finalY + borderRadius);
            ctx.lineTo(adjustedX + width, finalY + height - borderRadius);
            ctx.quadraticCurveTo(adjustedX + width, finalY + height, adjustedX + width - borderRadius, finalY + height);
            ctx.lineTo(adjustedX + borderRadius, finalY + height);
            ctx.quadraticCurveTo(adjustedX, finalY + height, adjustedX, finalY + height - borderRadius);
            ctx.lineTo(adjustedX, finalY + borderRadius);
            ctx.quadraticCurveTo(adjustedX, finalY, adjustedX + borderRadius, finalY);
        }
        ctx.closePath();
        ctx.clip();
        
        // Card color - special color for highlighted cards
        let isRed = card.suit === '♥' || card.suit === '♦';
        let textColor;
        
        if (highlightThreeSpades) {
            // Green for highlighted 3♠
            textColor = '#008800'; // Dark green
        } else if (isSpecialCard && isPlayerCard) {
            // Gold for 2s, Green for 3s
            textColor = card.rank === 2 ? '#B8860B' : '#008800';
        } else {
            // Normal colors
            textColor = isRed ? '#C80000' : '#000000';
        }
        
        // Adjust font sizes based on card size
        const scaleFactor = isHovered ? this.ANIMATIONS.hover.scale : 1;
        const rankFontSize = isPlayerCard ? `bold ${Math.floor(19 * scaleFactor)}px Arial` : `bold ${Math.floor(16 * scaleFactor)}px Arial`;
        const smallSuitFontSize = isPlayerCard ? `${Math.floor(22 * scaleFactor)}px Arial` : `${Math.floor(18 * scaleFactor)}px Arial`;
        const largeSuitFontSize = isPlayerCard ? `${Math.floor(34 * scaleFactor)}px Arial` : `${Math.floor(28 * scaleFactor)}px Arial`;
        
        // Draw rank in top-left
        ctx.font = rankFontSize;
        ctx.fillStyle = textColor;
        ctx.fillText(this.rankToSymbol(card.rank), adjustedX + textOffset * scaleFactor, finalY + (isPlayerCard ? 24 : 20) * scaleFactor);
        
        // Draw suit in top-left (small)
        ctx.font = smallSuitFontSize;
        ctx.fillText(card.suit, adjustedX + textOffset * scaleFactor, finalY + (isPlayerCard ? 48 : 40) * scaleFactor);
        
        // Draw large suit in center
        ctx.font = largeSuitFontSize;
        
        // Special treatment for special cards
        if (highlightThreeSpades || (isSpecialCard && isPlayerCard)) {
            // Add glow effect to center symbol
            ctx.save();
            const glowColor = highlightThreeSpades ? 'rgba(0, 255, 0, 0.7)' : 
                              (card.rank === 2 ? 'rgba(255, 215, 0, 0.7)' : 'rgba(0, 255, 0, 0.7)');
            ctx.shadowColor = glowColor;
            ctx.shadowBlur = 10;
            ctx.fillText(card.suit, adjustedX + width/2 - (isPlayerCard ? 10 : 8) * scaleFactor, finalY + height/2 + (isPlayerCard ? 12 : 10) * scaleFactor);
            ctx.restore();
        } else {
            ctx.fillText(card.suit, adjustedX + width/2 - (isPlayerCard ? 10 : 8) * scaleFactor, finalY + height/2 + (isPlayerCard ? 12 : 10) * scaleFactor);
        }
        
        // Draw rank in bottom-right (upside down)
        ctx.save();
        ctx.translate(adjustedX + width - textOffset * scaleFactor, finalY + height - textOffset * scaleFactor);
        ctx.rotate(Math.PI);
        ctx.font = rankFontSize;
        ctx.fillStyle = textColor;
        ctx.fillText(this.rankToSymbol(card.rank), 0, 0);
        ctx.restore();
        
        // Special indicator for special cards
        if ((highlightThreeSpades || (isSpecialCard && isPlayerCard)) && isPlayerCard) {
            // Draw a small indicator in top-right corner
            ctx.save();
            ctx.fillStyle = highlightThreeSpades ? '#00FF00' : 
                           (card.rank === 2 ? '#FFD700' : '#00FF00');
            ctx.font = `bold ${Math.floor(12 * scaleFactor)}px Arial`;
            const indicator = highlightThreeSpades ? '★' : (card.rank === 2 ? '✨' : '★');
            ctx.fillText(indicator, adjustedX + width - 20 * scaleFactor, finalY + 20 * scaleFactor);
            ctx.restore();
        }
        
        ctx.restore(); // Restore clip
        ctx.restore(); // Restore original context
        
        return {
            x: adjustedX,
            y: finalY,
            width: width,
            height: height,
            index: card.index || 0,
            isThreeSpades: isThreeSpades,
            highlightThreeSpades: highlightThreeSpades,
            isSpecialCard: isSpecialCard
        };
    },
    
    drawHand: function(ctx, hand, y, selectedCards = [], hoveredCard = -1, canvasWidth) {
        // REMOVED startX parameter - we always center
        const cardWidth = 72;
        const cardHeight = 101;
        
        const totalCards = hand.length;
        
        if (totalCards === 0) {
            return [];
        }
        
        // ===== ALWAYS CENTER ALL CARDS =====
        // Calculate available width (with padding)
        const availableWidth = canvasWidth - 60; // 30px padding on each side
        
        // Calculate optimal spacing
        let spacing;
        
        if (totalCards === 1) {
            // Single card - no spacing needed
            spacing = 0;
        } else if (totalCards <= 6) {
            // 2-6 cards: Comfortable spacing
            spacing = cardWidth + 20;
        } else if (totalCards <= 10) {
            // 7-10 cards: Moderate spacing
            spacing = cardWidth + 10;
        } else if (totalCards <= 14) {
            // 11-14 cards: Compact spacing
            spacing = cardWidth;
        } else if (totalCards <= 18) {
            // 15-18 cards: Tight spacing
            spacing = cardWidth - 10;
        } else {
            // 19+ cards: Very tight spacing
            spacing = cardWidth - 15;
        }
        
        // Calculate total width needed
        const totalWidth = (totalCards - 1) * spacing + cardWidth;
        
        // If total width exceeds available space, reduce spacing
        if (totalWidth > availableWidth && totalCards > 1) {
            spacing = (availableWidth - cardWidth) / (totalCards - 1);
            spacing = Math.max(cardWidth - 20, spacing); // Minimum spacing
        }
        
        // Recalculate total width with adjusted spacing
        const finalTotalWidth = (totalCards - 1) * spacing + cardWidth;
        
        // Calculate starting X to center all cards
        const startX = Math.max(30, (canvasWidth - finalTotalWidth) / 2);
        
        const cardRects = [];
        
        // Draw each card
        for (let i = 0; i < totalCards; i++) {
            const cardX = startX + i * spacing;
            
            const isSelected = selectedCards.includes(i);
            const isHovered = hoveredCard === i;
            
            // Save context for clipping
            ctx.save();
            
            // Clip to prevent text overflow
            ctx.beginPath();
            if (ctx.roundRect) {
                ctx.roundRect(cardX, y, cardWidth, cardHeight, 10);
            } else {
                const radius = 10;
                ctx.moveTo(cardX + radius, y);
                ctx.lineTo(cardX + cardWidth - radius, y);
                ctx.quadraticCurveTo(cardX + cardWidth, y, cardX + cardWidth, y + radius);
                ctx.lineTo(cardX + cardWidth, y + cardHeight - radius);
                ctx.quadraticCurveTo(cardX + cardWidth, y + cardHeight, cardX + cardWidth - radius, y + cardHeight);
                ctx.lineTo(cardX + radius, y + cardHeight);
                ctx.quadraticCurveTo(cardX, y + cardHeight, cardX, y + cardHeight - radius);
                ctx.lineTo(cardX, y + radius);
                ctx.quadraticCurveTo(cardX, y, cardX + radius, y);
            }
            ctx.closePath();
            ctx.clip();
            
            // Lift selected cards
            const drawY = isSelected ? y - 20 : y;
            
            // Draw the card
            const rect = this.drawCardFace(ctx, hand[i], cardX, drawY, isSelected, isHovered, false, true);
            rect.index = i;
            cardRects.push(rect);
            
            ctx.restore(); // Restore clipping
            
            // Selection indicator
            if (isSelected) {
                ctx.save();
                ctx.fillStyle = '#FFD700';
                ctx.beginPath();
                ctx.arc(cardX + cardWidth/2, y - 8, 6, 0, Math.PI * 2);
                ctx.fill();
                
                // Glow effect
                ctx.shadowColor = '#FFD700';
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
                ctx.restore();
            }
        }
        
        // Draw hand label
        ctx.save();
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.beginPath();
        ctx.roundRect(canvasWidth/2 - 60, y - 35, 120, 25, 8);
        ctx.fill();
        
        ctx.fillStyle = '#FFD700';
        ctx.font = 'bold 18px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Your Hand', canvasWidth/2, y - 22);
        ctx.restore();
        
        // Draw card count badge
        ctx.save();
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.beginPath();
        ctx.arc(canvasWidth - 40, y + cardHeight/2, 18, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = '#FFD700';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(totalCards.toString(), canvasWidth - 40, y + cardHeight/2);
        ctx.restore();
        
        return cardRects;
    },
        
    drawBotHand: function(ctx, cardCount, x, y, isCurrentTurn, canvasWidth, botIndex) {
        // Use botIndex parameter to determine which bot this is
        const botName = `Bot ${botIndex}`;
        
        // Bigger bot cards - increased size
        const cardWidth = 50;      // Increased from 40
        const cardHeight = 70;     // Increased from 56
        
        // Show limited number of cards for bots
        const maxCards = Math.min(cardCount, 7); // Show more cards
        
        // Overlap cards for compact display
        const overlap = 15;
        const spacing = cardWidth - overlap;
        
        // Calculate total width for centering
        const totalWidth = Math.min(maxCards, cardCount) * spacing - overlap + cardWidth;
        const startX = x + (150 - totalWidth) / 2; // Center within bot's area
        
        for (let i = 0; i < maxCards; i++) {
            const cardX = startX + i * spacing;
            
            // Draw card back
            ctx.save();
            
            // Gradient background - different colors for current turn
            const gradient = ctx.createLinearGradient(
                cardX, y, 
                cardX + cardWidth, y + cardHeight
            );
            
            if (isCurrentTurn) {
                // Gold gradient for current bot's turn
                gradient.addColorStop(0, '#D4AF37');
                gradient.addColorStop(0.5, '#B8860B');
                gradient.addColorStop(1, '#8B6914');
            } else {
                // Green gradient for inactive bots
                gradient.addColorStop(0, '#228B22');
                gradient.addColorStop(0.5, '#006400');
                gradient.addColorStop(1, '#004d00');
            }
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            
            if (ctx.roundRect) {
                ctx.roundRect(cardX, y, cardWidth, cardHeight, 8);
            } else {
                const radius = 8;
                ctx.moveTo(cardX + radius, y);
                ctx.lineTo(cardX + cardWidth - radius, y);
                ctx.quadraticCurveTo(cardX + cardWidth, y, cardX + cardWidth, y + radius);
                ctx.lineTo(cardX + cardWidth, y + cardHeight - radius);
                ctx.quadraticCurveTo(cardX + cardWidth, y + cardHeight, cardX + cardWidth - radius, y + cardHeight);
                ctx.lineTo(cardX + radius, y + cardHeight);
                ctx.quadraticCurveTo(cardX, y + cardHeight, cardX, y + cardHeight - radius);
                ctx.lineTo(cardX, y + radius);
                ctx.quadraticCurveTo(cardX, y, cardX + radius, y);
            }
            ctx.closePath();
            ctx.fill();
            
            // Border with glow for current turn
            if (isCurrentTurn) {
                ctx.strokeStyle = '#FFD700';
                ctx.lineWidth = 3;
                // Add glow effect
                ctx.shadowColor = 'rgba(255, 215, 0, 0.7)';
                ctx.shadowBlur = 10;
                ctx.stroke();
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
            } else {
                ctx.strokeStyle = '#A67C00';
                ctx.lineWidth = 2;
                ctx.stroke();
            }
            
            // Vietnamese pattern for bot cards
            ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
            
            // Draw simple pattern
            const centerX = cardX + cardWidth/2;
            const centerY = y + cardHeight/2;
            
            // Draw small diamond pattern
            ctx.beginPath();
            ctx.moveTo(centerX, centerY - 8);
            ctx.lineTo(centerX + 8, centerY);
            ctx.lineTo(centerX, centerY + 8);
            ctx.lineTo(centerX - 8, centerY);
            ctx.closePath();
            ctx.fill();
            
            // Draw small center dot
            ctx.beginPath();
            ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 215, 0, 0.4)';
            ctx.fill();
            
            // Add card corner indicators
            ctx.font = 'bold 12px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
            
            // Top-left corner
            ctx.fillText('♠', cardX + 10, y + 12);
            // Top-right corner
            ctx.fillText('♥', cardX + cardWidth - 10, y + 12);
            // Bottom-left corner
            ctx.fillText('♦', cardX + 10, y + cardHeight - 12);
            // Bottom-right corner
            ctx.fillText('♣', cardX + cardWidth - 10, y + cardHeight - 12);
            
            // Inner border decoration
            ctx.strokeStyle = 'rgba(255, 215, 0, 0.2)';
            ctx.lineWidth = 1;
            const innerPadding = 8;
            ctx.beginPath();
            ctx.moveTo(cardX + innerPadding, y + innerPadding);
            ctx.lineTo(cardX + cardWidth - innerPadding, y + innerPadding);
            ctx.lineTo(cardX + cardWidth - innerPadding, y + cardHeight - innerPadding);
            ctx.lineTo(cardX + innerPadding, y + cardHeight - innerPadding);
            ctx.closePath();
            ctx.stroke();
            
            ctx.restore();
        }
        
        // Show count if bot has more cards than we can display
        if (cardCount > maxCards) {
            ctx.save();
            
            const badgeX = startX + maxCards * spacing - 5;
            const badgeY = y + cardHeight/2;
            
            // Badge background
            ctx.fillStyle = isCurrentTurn ? 'rgba(0, 0, 0, 0.9)' : 'rgba(0, 0, 0, 0.7)';
            ctx.beginPath();
            ctx.arc(badgeX, badgeY, 14, 0, Math.PI * 2);
            ctx.fill();
            
            if (isCurrentTurn) {
                // Glow for current bot
                ctx.shadowColor = '#FFD700';
                ctx.shadowBlur = 8;
                ctx.strokeStyle = '#FFD700';
                ctx.lineWidth = 2;
                ctx.stroke();
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
            }
            
            // Badge text
            ctx.fillStyle = '#FFD700';
            ctx.font = 'bold 14px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(`+${cardCount - maxCards}`, badgeX, badgeY);
            
            ctx.restore();
        }
        
        // Draw bot's name above cards
        ctx.save();
        ctx.fillStyle = isCurrentTurn ? '#FFD700' : '#FFFFFF';
        ctx.font = isCurrentTurn ? 'bold 18px Arial' : 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        
        // Calculate center of bot's hand
        const handCenterX = startX + (Math.min(maxCards, cardCount) * spacing) / 2;
        
        // Use the actual bot name passed as parameter
        ctx.fillText(botName, handCenterX, y - 5);
        
        // Card count below
        ctx.font = '14px Arial';
        ctx.fillStyle = '#A0AEC0';
        ctx.fillText(`${cardCount} cards`, handCenterX, y + cardHeight + 15);
        ctx.restore();
        
        return {
            x: startX,
            y: y,
            width: Math.min(maxCards, cardCount) * spacing + cardWidth,
            height: cardHeight
        };
    },
    
    // Draw cards in the play area - NORMAL SIZE
    drawPlayArea: function(ctx, cards, centerX, centerY, canvasWidth) {
        if (!cards || cards.length === 0) return;
        
        const cardWidth = 60;      // Normal size for play area
        const cardHeight = 84;     // Normal size for play area
        
        // Calculate spacing based on number of cards
        let overlap;
        if (cards.length <= 8) {
            overlap = 10;
        } else if (cards.length <= 12) {
            overlap = 15;
        } else {
            overlap = 20;
        }
        
        // Calculate total width of the played cards
        const totalWidth = cards.length * (cardWidth - overlap) + overlap;
        const startX = centerX - totalWidth/2;
        
        // Draw each card with clipping to prevent text overflow
        for (let i = 0; i < cards.length; i++) {
            const cardX = startX + i * (cardWidth - overlap);
            
            // Save context and clip
            ctx.save();
            ctx.beginPath();
            if (ctx.roundRect) {
                ctx.roundRect(cardX, centerY - cardHeight/2, cardWidth, cardHeight, 8);
            } else {
                const y = centerY - cardHeight/2;
                ctx.moveTo(cardX + 8, y);
                ctx.lineTo(cardX + cardWidth - 8, y);
                ctx.quadraticCurveTo(cardX + cardWidth, y, cardX + cardWidth, y + 8);
                ctx.lineTo(cardX + cardWidth, y + cardHeight - 8);
                ctx.quadraticCurveTo(cardX + cardWidth, y + cardHeight, cardX + cardWidth - 8, y + cardHeight);
                ctx.lineTo(cardX + 8, y + cardHeight);
                ctx.quadraticCurveTo(cardX, y + cardHeight, cardX, y + cardHeight - 8);
                ctx.lineTo(cardX, y + 8);
                ctx.quadraticCurveTo(cardX, y, cardX + 8, y);
            }
            ctx.closePath();
            ctx.clip();
            
            // Draw card with slight elevation
            ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
            ctx.shadowBlur = 10;
            ctx.shadowOffsetY = 5;
            
            // Draw card - pass false for isPlayerCard (normal size)
            this.drawCardFace(ctx, cards[i], cardX, centerY - cardHeight/2, false, false, true, false);
            
            ctx.restore();
        }
        
        // Draw play highlight
        ctx.save();
        ctx.globalAlpha = 0.2;
        ctx.fillStyle = '#FFD700';
        ctx.beginPath();
        const highlightRadius = Math.max(totalWidth/2 + 20, cardHeight/2 + 10);
        ctx.arc(centerX, centerY, highlightRadius, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    },
    
    // Draw automatic win indicator
    drawAutomaticWinIndicator: function(ctx, playerName, reason, x, y, canvasWidth) {
        ctx.save();
        
        // Draw warning banner
        const bannerWidth = 500;
        const bannerHeight = 80;
        const bannerX = (canvasWidth - bannerWidth) / 2;
        const bannerY = 50;
        
        // Background with gold gradient
        const gradient = ctx.createLinearGradient(bannerX, bannerY, bannerX, bannerY + bannerHeight);
        gradient.addColorStop(0, 'rgba(255, 215, 0, 0.9)');
        gradient.addColorStop(0.5, 'rgba(255, 165, 0, 0.9)');
        gradient.addColorStop(1, 'rgba(255, 140, 0, 0.9)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        if (ctx.roundRect) {
            ctx.roundRect(bannerX, bannerY, bannerWidth, bannerHeight, 20);
        } else {
            ctx.moveTo(bannerX + 20, bannerY);
            ctx.lineTo(bannerX + bannerWidth - 20, bannerY);
            ctx.quadraticCurveTo(bannerX + bannerWidth, bannerY, bannerX + bannerWidth, bannerY + 20);
            ctx.lineTo(bannerX + bannerWidth, bannerY + bannerHeight - 20);
            ctx.quadraticCurveTo(bannerX + bannerWidth, bannerY + bannerHeight, bannerX + bannerWidth - 20, bannerY + bannerHeight);
            ctx.lineTo(bannerX + 20, bannerY + bannerHeight);
            ctx.quadraticCurveTo(bannerX, bannerY + bannerHeight, bannerX, bannerY + bannerHeight - 20);
            ctx.lineTo(bannerX, bannerY + 20);
            ctx.quadraticCurveTo(bannerX, bannerY, bannerX + 20, bannerY);
        }
        ctx.closePath();
        ctx.fill();
        
        // Red border
        ctx.strokeStyle = '#FF0000';
        ctx.lineWidth = 4;
        ctx.stroke();
        
        // Add inner glow
        ctx.shadowColor = 'rgba(255, 255, 0, 0.7)';
        ctx.shadowBlur = 20;
        ctx.stroke();
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        
        // Text
        ctx.fillStyle = '#000000';
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Title
        ctx.fillText(`🏆 ${playerName.toUpperCase()} WINS AUTOMATICALLY! 🏆`, canvasWidth / 2, bannerY + 30);
        
        // Reason
        ctx.font = 'bold 18px Arial';
        ctx.fillStyle = '#8B0000';
        ctx.fillText(`Reason: ${reason.replace('has ', '').toUpperCase()}`, canvasWidth / 2, bannerY + 60);
        
        ctx.restore();
    },
    
    // Draw selected cards indicator
    drawSelectedIndicator: function(ctx, count, x, y) {
        if (count === 0) return;
        
        ctx.save();
        
        // Draw indicator circle with Vietnamese-inspired gold
        ctx.fillStyle = '#D4AF37';
        ctx.beginPath();
        ctx.arc(x, y, 15, 0, Math.PI * 2);
        ctx.fill();
        
        // Add a subtle border
        ctx.strokeStyle = '#FFD700';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Add glow
        ctx.shadowColor = 'rgba(255, 215, 0, 0.5)';
        ctx.shadowBlur = 10;
        ctx.stroke();
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        
        // Draw count
        ctx.fillStyle = '#000000';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(count.toString(), x, y);
        
        ctx.restore();
    },
    
    // Draw game information overlay
    drawGameInfo: function(ctx, gameState, canvasWidth, canvasHeight) {
        if (!gameState) return;
        
        ctx.save();
        
        // Get round number - check multiple possible properties
        let roundNumber = 1;
        
        // Check various possible locations for round number
        if (gameState.round !== undefined) {
            roundNumber = gameState.round;
        } else if (gameState.round_number !== undefined) {
            roundNumber = gameState.round_number;
        } else if (gameState.summary && gameState.summary.round !== undefined) {
            roundNumber = gameState.summary.round;
        } else if (gameState.roundNumber !== undefined) {
            roundNumber = gameState.roundNumber;
        }
        
        // Draw round info
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.font = 'bold 18px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`Round ${roundNumber}`, canvasWidth / 2, 104);
        
        // Get current player name
        let currentPlayerName = null;
        let isPlayerTurn = false;
        
        if (gameState.current_player) {
            currentPlayerName = gameState.current_player;
            isPlayerTurn = gameState.is_player_turn;
        } else if (gameState.currentPlayer) {
            currentPlayerName = gameState.currentPlayer;
            isPlayerTurn = gameState.isPlayerTurn;
        }
        

        
        // Draw 3♠ rule info if applicable
        let rulesInfo = gameState.rules_info || gameState.rulesInfo;
        if (rulesInfo && rulesInfo.requires_three_spades) {
            ctx.fillStyle = '#00FF00';
            ctx.font = 'bold 16px Arial';
            
            const threeSpadesPlayer = rulesInfo.three_spades_player || rulesInfo.threeSpadesPlayer;
            if (threeSpadesPlayer && threeSpadesPlayer.includes('You')) {
                ctx.fillText('You have 3♠! You must include it in your first play.', canvasWidth / 2, 80);
            } else if (threeSpadesPlayer) {
                ctx.fillText(`${threeSpadesPlayer} has 3♠ and starts the game.`, canvasWidth / 2, 80);
            }
        }
        
        ctx.restore();
    },
    // ===== ANIMATION SYSTEM =====
    
    // Create bot play animation with highlighting
    createBotPlayAnimation: function(botIndex, card, fromX, fromY, toX, toY) {
        return {
            botIndex: botIndex,
            card: card,
            fromX: fromX,
            fromY: fromY,
            toX: toX,
            toY: toY,
            startTime: Date.now(),
            duration: 800,
            progress: 0,
            isComplete: false,
            
            update: function() {
                const elapsed = Date.now() - this.startTime;
                this.progress = Math.min(elapsed / this.duration, 1);
                
                // Cubic easing function for smooth animation
                const easedProgress = this.progress < 0.5 
                    ? 4 * this.progress * this.progress * this.progress
                    : 1 - Math.pow(-2 * this.progress + 2, 3) / 2;
                
                this.currentX = this.fromX + (this.toX - this.fromX) * easedProgress;
                this.currentY = this.fromY + (this.toY - this.fromY) * easedProgress;
                
                this.isComplete = this.progress >= 1;
                return !this.isComplete;
            },
            
            draw: function(ctx) {
                if (this.isComplete) return;
                
                ctx.save();
                
                // Special effect for 3♠
                const isThreeSpades = this.card.rank === 3 && this.card.suit === '♠';
                const isTwo = this.card.rank === 2;
                
                if (isThreeSpades) {
                    // Green glow for 3♠
                    ctx.shadowColor = 'rgba(0, 255, 0, 0.7)';
                    ctx.shadowBlur = 20;
                    ctx.shadowOffsetY = 5;
                } else if (isTwo) {
                    // Gold glow for 2s
                    ctx.shadowColor = 'rgba(255, 215, 0, 0.7)';
                    ctx.shadowBlur = 25;
                    ctx.shadowOffsetY = 5;
                } else {
                    // Normal glow
                    ctx.shadowColor = 'rgba(78, 205, 196, 0.7)';
                    ctx.shadowBlur = 20;
                    ctx.shadowOffsetY = 5;
                }
                
                // Draw the card at current position
                cardRenderer.drawCardFace(ctx, this.card, this.currentX, this.currentY, false, false, true, false);
                
                // Draw a trail effect
                if (this.progress < 0.9) {
                    ctx.globalAlpha = 0.3 * (1 - this.progress);
                    ctx.shadowBlur = 30;
                    cardRenderer.drawCardFace(ctx, this.card, this.currentX, this.currentY, false, false, true, false);
                }
                
                ctx.restore();
            }
        };
    },
    
    // Create card flip animation (for bot reveals)
    createCardFlipAnimation: function(card, x, y) {
        return {
            card: card,
            x: x,
            y: y,
            startTime: Date.now(),
            duration: 600,
            progress: 0,
            isComplete: false,
            isFlipped: false,
            
            update: function() {
                const elapsed = Date.now() - this.startTime;
                this.progress = Math.min(elapsed / this.duration, 1);
                this.isFlipped = this.progress > 0.5;
                this.isComplete = this.progress >= 1;
                return !this.isComplete;
            },
            
            draw: function(ctx) {
                if (this.isComplete) return;
                
                ctx.save();
                
                const flipProgress = this.progress < 0.5 ? this.progress * 2 : (1 - this.progress) * 2;
                const scaleX = Math.abs(1 - flipProgress);
                
                // Apply scale transformation
                ctx.translate(this.x + 30, this.y + 42);
                ctx.scale(scaleX, 1);
                ctx.translate(-(this.x + 30), -(this.y + 42));
                
                if (this.isFlipped) {
                    // Draw card face
                    cardRenderer.drawCardFace(ctx, this.card, this.x, this.y, false, false, true, false);
                } else {
                    // Draw card back
                    ctx.fillStyle = '#145A32';
                    ctx.beginPath();
                    if (ctx.roundRect) {
                        ctx.roundRect(this.x, this.y, 60, 84, 8);
                    } else {
                        ctx.moveTo(this.x + 8, this.y);
                        ctx.lineTo(this.x + 52, this.y);
                        ctx.quadraticCurveTo(this.x + 60, this.y, this.x + 60, this.y + 8);
                        ctx.lineTo(this.x + 60, this.y + 76);
                        ctx.quadraticCurveTo(this.x + 60, this.y + 84, this.x + 52, this.y + 84);
                        ctx.lineTo(this.x + 8, this.y + 84);
                        ctx.quadraticCurveTo(this.x, this.y + 84, this.x, this.y + 76);
                        ctx.lineTo(this.x, this.y + 8);
                        ctx.quadraticCurveTo(this.x, this.y, this.x + 8, this.y);
                    }
                    ctx.closePath();
                    ctx.fill();
                    
                    // Draw pattern
                    ctx.fillStyle = 'rgba(255, 215, 0, 0.2)';
                    ctx.font = 'bold 20px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('♠', this.x + 30, this.y + 42);
                }
                
                ctx.restore();
            }
        };
    },
    
    // Draw multiple bot animations
    drawBotAnimations: function(ctx, animations) {
        animations.forEach(anim => {
            if (!anim.isComplete) {
                anim.draw(ctx);
            }
        });
    },
    
    // Update all animations
    updateAnimations: function(animations) {
        return animations.filter(anim => anim.update());
    },
    
    // Create card deal animation (for initial deal)
    createDealAnimation: function(card, fromX, fromY, toX, toY, delay = 0) {
        return {
            card: card,
            fromX: fromX,
            fromY: fromY,
            toX: toX,
            toY: toY,
            startTime: Date.now() + delay,
            duration: 500,
            progress: 0,
            isComplete: false,
            
            update: function() {
                if (Date.now() < this.startTime) return true;
                
                const elapsed = Date.now() - this.startTime;
                this.progress = Math.min(elapsed / this.duration, 1);
                
                // Bounce easing
                const easedProgress = this.progress < 0.5
                    ? 2 * this.progress * this.progress
                    : 1 - Math.pow(-2 * this.progress + 2, 2) / 2;
                
                this.currentX = this.fromX + (this.toX - this.fromX) * easedProgress;
                this.currentY = this.fromY + (this.toY - this.fromY) * easedProgress;
                
                this.isComplete = this.progress >= 1;
                return !this.isComplete;
            },
            
            draw: function(ctx) {
                if (this.isComplete || Date.now() < this.startTime) return;
                
                ctx.save();
                
                // Add slight rotation during deal
                const rotation = Math.sin(this.progress * Math.PI) * 0.1;
                ctx.translate(this.currentX + 30, this.currentY + 42);
                ctx.rotate(rotation);
                ctx.translate(-(this.currentX + 30), -(this.currentY + 42));
                
                cardRenderer.drawCardFace(ctx, this.card, this.currentX, this.currentY, false, false, true, true);
                
                ctx.restore();
            }
        };
    },
    
    // Create special animation for 3♠ reveal
    createThreeSpadesAnimation: function(card, x, y) {
        return {
            card: card,
            x: x,
            y: y,
            startTime: Date.now(),
            duration: 1500,
            progress: 0,
            isComplete: false,
            
            update: function() {
                const elapsed = Date.now() - this.startTime;
                this.progress = Math.min(elapsed / this.duration, 1);
                this.isComplete = this.progress >= 1;
                return !this.isComplete;
            },
            
            draw: function(ctx) {
                if (this.isComplete) return;
                
                ctx.save();
                
                // Pulse effect
                const pulse = Math.sin(this.progress * Math.PI * 4) * 0.5 + 0.5;
                const scale = 1 + pulse * 0.1;
                
                ctx.translate(this.x + 30, this.y + 42);
                ctx.scale(scale, scale);
                ctx.translate(-(this.x + 30), -(this.y + 42));
                
                // Intense green glow
                ctx.shadowColor = `rgba(0, 255, 0, ${0.3 + pulse * 0.4})`;
                ctx.shadowBlur = 20 + pulse * 15;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 0;
                
                // Draw card with special border
                const cardRect = { x: this.x, y: this.y, width: 60, height: 84 };
                
                // Draw glowing background
                ctx.fillStyle = `rgba(0, 255, 0, ${0.1 + pulse * 0.1})`;
                ctx.beginPath();
                ctx.roundRect(this.x - 10, this.y - 10, 80, 104, 12);
                ctx.fill();
                
                // Draw the card
                cardRenderer.drawCardFace(ctx, this.card, this.x, this.y, false, false, true, false);
                
                // Draw sparkles
                ctx.fillStyle = `rgba(255, 255, 255, ${pulse * 0.8})`;
                const sparkleCount = 8;
                for (let i = 0; i < sparkleCount; i++) {
                    const angle = (i / sparkleCount) * Math.PI * 2 + this.progress * Math.PI * 2;
                    const radius = 50;
                    const sparkleX = this.x + 30 + Math.cos(angle) * radius;
                    const sparkleY = this.y + 42 + Math.sin(angle) * radius;
                    
                    ctx.beginPath();
                    ctx.arc(sparkleX, sparkleY, 3, 0, Math.PI * 2);
                    ctx.fill();
                }
                
                ctx.restore();
                
                // Draw "3♠!" text
                if (pulse > 0.5) {
                    ctx.save();
                    ctx.fillStyle = `rgba(0, 255, 0, ${pulse})`;
                    ctx.font = 'bold 24px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('3♠!', this.x + 30, this.y - 20);
                    ctx.restore();
                }
            }
        };
    }
};

// Make cardRenderer available globally
if (typeof window !== 'undefined') {
    window.cardRenderer = cardRenderer;
}