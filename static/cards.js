// /static/cards.js - CARD RENDERER FOR TIEN LEN MIEN NAM
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
        }
    },
    
    // Convert rank number to display symbol
    rankToSymbol: function(rank) {
        if (rank === 11) return 'J';
        if (rank === 12) return 'Q';
        if (rank === 13) return 'K';
        if (rank === 14) return 'A';
        if (rank === 15) return '2';
        return rank.toString();
    },
    
    // Draw a single card face with enhanced hover effects
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
        
        // Apply shadow if hovering
        if (shadowEffect) {
            ctx.shadowColor = shadowEffect.color;
            ctx.shadowBlur = shadowEffect.blur;
            ctx.shadowOffsetX = shadowEffect.offsetX;
            ctx.shadowOffsetY = shadowEffect.offsetY;
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
        
        // Clear shadow for border
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        
        // Card border with glow effect
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
        
        // Card color (red for hearts/diamonds, black for clubs/spades)
        const isRed = card.suit === '♥' || card.suit === '♦';
        ctx.fillStyle = isRed ? '#C80000' : '#000000';
        
        // Adjust font sizes based on card size
        const scaleFactor = isHovered ? this.ANIMATIONS.hover.scale : 1;
        const rankFontSize = isPlayerCard ? `bold ${Math.floor(19 * scaleFactor)}px Arial` : `bold ${Math.floor(16 * scaleFactor)}px Arial`;
        const smallSuitFontSize = isPlayerCard ? `${Math.floor(22 * scaleFactor)}px Arial` : `${Math.floor(18 * scaleFactor)}px Arial`;
        const largeSuitFontSize = isPlayerCard ? `${Math.floor(34 * scaleFactor)}px Arial` : `${Math.floor(28 * scaleFactor)}px Arial`;
        
        // Draw rank in top-left
        ctx.font = rankFontSize;
        ctx.fillText(this.rankToSymbol(card.rank), adjustedX + textOffset * scaleFactor, finalY + (isPlayerCard ? 24 : 20) * scaleFactor);
        
        // Draw suit in top-left (small)
        ctx.font = smallSuitFontSize;
        ctx.fillText(card.suit, adjustedX + textOffset * scaleFactor, finalY + (isPlayerCard ? 48 : 40) * scaleFactor);
        
        // Draw large suit in center
        ctx.font = largeSuitFontSize;
        ctx.fillText(card.suit, adjustedX + width/2 - (isPlayerCard ? 10 : 8) * scaleFactor, finalY + height/2 + (isPlayerCard ? 12 : 10) * scaleFactor);
        
        // Draw rank in bottom-right (upside down)
        ctx.save();
        ctx.translate(adjustedX + width - textOffset * scaleFactor, finalY + height - textOffset * scaleFactor);
        ctx.rotate(Math.PI);
        ctx.font = rankFontSize;
        ctx.fillText(this.rankToSymbol(card.rank), 0, 0);
        ctx.restore();
        
        ctx.restore(); // Restore clip
        ctx.restore(); // Restore original context
        
        return {
            x: adjustedX,
            y: finalY,
            width: width,
            height: height,
            index: card.index || 0
        };
    },
    
    // Draw player's hand - USING BIGGER CARDS
    drawHand: function(ctx, hand, startX, y, selectedCards = [], hoveredCard = -1, canvasWidth) {
        const cardWidth = 72;      // Bigger cards for player
        const cardHeight = 101;    // Bigger cards for player
        const overlap = 30;        // More overlap for bigger cards
        const maxCardsInRow = Math.min(hand.length, Math.floor((canvasWidth - 100) / (cardWidth - overlap)));
        
        const cardRects = [];
        
        // Calculate spacing to center the hand
        const totalWidth = Math.min(hand.length * (cardWidth - overlap) + overlap, canvasWidth - 100);
        const actualStartX = startX + (canvasWidth - 100 - totalWidth) / 2;
        
        // Draw cards from left to right
        for (let i = 0; i < hand.length; i++) {
            // Calculate position with overlap
            let cardX = actualStartX + i * (cardWidth - overlap);
            
            const isSelected = selectedCards.includes(i);
            const isHovered = hoveredCard === i;
            
            // Save the area for this card to prevent overlapping drawing
            ctx.save();
            
            // Clip to card area to prevent overflow
            ctx.beginPath();
            if (ctx.roundRect) {
                ctx.roundRect(cardX, y, cardWidth, cardHeight, 10);
            } else {
                ctx.moveTo(cardX + 10, y);
                ctx.lineTo(cardX + cardWidth - 10, y);
                ctx.quadraticCurveTo(cardX + cardWidth, y, cardX + cardWidth, y + 10);
                ctx.lineTo(cardX + cardWidth, y + cardHeight - 10);
                ctx.quadraticCurveTo(cardX + cardWidth, y + cardHeight, cardX + cardWidth - 10, y + cardHeight);
                ctx.lineTo(cardX + 10, y + cardHeight);
                ctx.quadraticCurveTo(cardX, y + cardHeight, cardX, y + cardHeight - 10);
                ctx.lineTo(cardX, y + 10);
                ctx.quadraticCurveTo(cardX, y, cardX + 10, y);
            }
            ctx.closePath();
            ctx.clip();
            
            // Adjust Y position for selected cards
            const drawY = isSelected ? y - 18 : y;
            
            // Draw the card - pass true for isPlayerCard
            const rect = this.drawCardFace(ctx, hand[i], cardX, drawY, isSelected, isHovered, false, true);
            rect.index = i;
            cardRects.push(rect);
            
            ctx.restore(); // Restore clipping
        }
        
        // Now draw selected cards on top with their lift effect
        for (let i = 0; i < hand.length; i++) {
            if (selectedCards.includes(i)) {
                const cardX = actualStartX + i * (cardWidth - overlap);
                const drawY = y - 18; // Selected cards float above
                
                // Save and set composite operation to draw on top
                ctx.save();
                ctx.globalCompositeOperation = 'source-over';
                
                // Draw card with selection highlight
                this.drawCardFace(ctx, hand[i], cardX, drawY, true, false, false, true);
                
                ctx.restore();
            }
        }
        
        return cardRects;
    },
    
    // Draw bot's hand (as card backs) - NORMAL SIZE
    drawBotHand: function(ctx, cardCount, x, y, isCurrentTurn, canvasWidth) {
        const cardWidth = 60;      // Normal size for bot cards
        const cardHeight = 84;     // Normal size for bot cards
        const overlap = 15;
        const maxCards = Math.min(cardCount, Math.floor((canvasWidth * 0.3) / (cardWidth - overlap)));
        
        for (let i = 0; i < maxCards; i++) {
            const cardX = x + i * (cardWidth - overlap);
            
            // Draw card back
            ctx.save();
            
            // Card back with rich Vietnamese-inspired colors
            ctx.fillStyle = isCurrentTurn ? '#0E4D28' : '#145A32';
            ctx.beginPath();
            if (ctx.roundRect) {
                ctx.roundRect(cardX, y, cardWidth, cardHeight, 8);
            } else {
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
            ctx.fill();
            
            // Gold border for current turn
            ctx.strokeStyle = isCurrentTurn ? '#FFD700' : '#D4AF37';
            ctx.lineWidth = isCurrentTurn ? 3 : 2;
            
            // Add glow to current bot's turn
            if (isCurrentTurn) {
                ctx.shadowColor = 'rgba(255, 215, 0, 0.5)';
                ctx.shadowBlur = 10;
            }
            
            ctx.stroke();
            
            // Clear shadow
            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;
            
            // Vietnamese-inspired pattern
            ctx.fillStyle = 'rgba(255, 215, 0, 0.2)';
            
            // Draw lotus flower pattern
            const centerX = cardX + cardWidth/2;
            const centerY = y + cardHeight/2;
            
            // Draw 8-petal lotus
            ctx.beginPath();
            for (let j = 0; j < 8; j++) {
                const angle = (j * Math.PI) / 4;
                const petalX = centerX + Math.cos(angle) * 15;
                const petalY = centerY + Math.sin(angle) * 15;
                
                if (j === 0) {
                    ctx.moveTo(petalX, petalY);
                } else {
                    ctx.lineTo(petalX, petalY);
                }
            }
            ctx.closePath();
            ctx.fill();
            
            // Center circle with gold color
            ctx.beginPath();
            ctx.arc(centerX, centerY, 6, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(212, 175, 55, 0.4)';
            ctx.fill();
            
            // Add subtle Vietnamese patterns in corners
            ctx.font = 'bold 12px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            
            // Vietnamese lucky symbols in corners
            ctx.fillText('🎋', cardX + 15, y + 15);
            ctx.fillText('★', cardX + cardWidth - 15, y + 15);
            ctx.fillText('🐉', cardX + 15, y + cardHeight - 15);
            ctx.fillText('🐢', cardX + cardWidth - 15, y + cardHeight - 15);
            
            // Add subtle border pattern
            ctx.strokeStyle = 'rgba(212, 175, 55, 0.3)';
            ctx.lineWidth = 1;
            const borderPadding = 12;
            ctx.beginPath();
            ctx.moveTo(cardX + borderPadding, y + borderPadding);
            ctx.lineTo(cardX + cardWidth - borderPadding, y + borderPadding);
            ctx.lineTo(cardX + cardWidth - borderPadding, y + cardHeight - borderPadding);
            ctx.lineTo(cardX + borderPadding, y + cardHeight - borderPadding);
            ctx.closePath();
            ctx.stroke();
            
            ctx.restore();
        }
        
        // If there are more cards than we can show, indicate with a number
        if (cardCount > maxCards) {
            ctx.fillStyle = 'white';
            ctx.font = 'bold 14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`+${cardCount - maxCards}`, x + maxCards * (cardWidth - overlap) + cardWidth/2, y + cardHeight/2);
        }
    },
    
    // Draw cards in the play area - NORMAL SIZE
    drawPlayArea: function(ctx, cards, centerX, centerY, canvasWidth) {
        if (!cards || cards.length === 0) return;
        
        const cardWidth = 60;      // Normal size for play area
        const cardHeight = 84;     // Normal size for play area
        const overlap = 20;
        
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
        
        // Draw count
        ctx.fillStyle = '#000000';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(count.toString(), x, y);
        
        ctx.restore();
    },
    
    // ===== ANIMATION SYSTEM =====
    
    // Create bot play animation
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
                
                // Add a glow effect during animation
                ctx.shadowColor = 'rgba(78, 205, 196, 0.7)';
                ctx.shadowBlur = 20;
                ctx.shadowOffsetY = 5;
                
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
    }
};

// Make cardRenderer available globally
if (typeof window !== 'undefined') {
    window.cardRenderer = cardRenderer;
}