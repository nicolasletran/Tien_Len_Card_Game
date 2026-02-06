// /static/cards.js - CARD RENDERER FOR TIEN LEN MIEN NAM
const cardRenderer = {
    // Convert rank number to display symbol
    rankToSymbol: function(rank) {
        if (rank === 11) return 'J';
        if (rank === 12) return 'Q';
        if (rank === 13) return 'K';
        if (rank === 14) return 'A';
        if (rank === 15) return '2';
        return rank.toString();
    },
    
    // Draw a single card face - BIGGER FOR PLAYER HAND
    drawCardFace: function(ctx, card, x, y, isSelected = false, isHovered = false, isAnimating = false, isPlayerCard = true) {
        // Use bigger size for player cards, normal for others
        const width = isPlayerCard ? 72 : 60;
        const height = isPlayerCard ? 101 : 84;
        const borderRadius = isPlayerCard ? 10 : 8;
        const textOffset = isPlayerCard ? 10 : 8;
        
        // Save context
        ctx.save();
        
        // Position for selection animation
        const liftAmount = isPlayerCard ? 18 : 15;
        const drawY = isSelected ? y - liftAmount : y;
        
        // Draw card background with rounded corners
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        if (ctx.roundRect) {
            ctx.roundRect(x, drawY, width, height, borderRadius);
        } else {
            // Fallback for browsers without roundRect
            ctx.moveTo(x + borderRadius, drawY);
            ctx.lineTo(x + width - borderRadius, drawY);
            ctx.quadraticCurveTo(x + width, drawY, x + width, drawY + borderRadius);
            ctx.lineTo(x + width, drawY + height - borderRadius);
            ctx.quadraticCurveTo(x + width, drawY + height, x + width - borderRadius, drawY + height);
            ctx.lineTo(x + borderRadius, drawY + height);
            ctx.quadraticCurveTo(x, drawY + height, x, drawY + height - borderRadius);
            ctx.lineTo(x, drawY + borderRadius);
            ctx.quadraticCurveTo(x, drawY, x + borderRadius, drawY);
        }
        ctx.closePath();
        ctx.fill();
        
        // Card border
        ctx.strokeStyle = isSelected ? '#FFD700' : (isHovered ? '#4ECDC4' : '#CCCCCC');
        ctx.lineWidth = isSelected ? 3 : (isHovered ? 2 : 1);
        ctx.stroke();
        
        // Clip the drawing area to prevent text from overflowing
        ctx.save();
        ctx.beginPath();
        if (ctx.roundRect) {
            ctx.roundRect(x, drawY, width, height, borderRadius);
        } else {
            ctx.moveTo(x + borderRadius, drawY);
            ctx.lineTo(x + width - borderRadius, drawY);
            ctx.quadraticCurveTo(x + width, drawY, x + width, drawY + borderRadius);
            ctx.lineTo(x + width, drawY + height - borderRadius);
            ctx.quadraticCurveTo(x + width, drawY + height, x + width - borderRadius, drawY + height);
            ctx.lineTo(x + borderRadius, drawY + height);
            ctx.quadraticCurveTo(x, drawY + height, x, drawY + height - borderRadius);
            ctx.lineTo(x, drawY + borderRadius);
            ctx.quadraticCurveTo(x, drawY, x + borderRadius, drawY);
        }
        ctx.closePath();
        ctx.clip();
        
        // Card color (red for hearts/diamonds, black for clubs/spades)
        const isRed = card.suit === '♥' || card.suit === '♦';
        ctx.fillStyle = isRed ? '#C80000' : '#000000';
        
        // Adjust font sizes based on card size
        const rankFontSize = isPlayerCard ? 'bold 19px Arial' : 'bold 16px Arial';
        const smallSuitFontSize = isPlayerCard ? '22px Arial' : '18px Arial';
        const largeSuitFontSize = isPlayerCard ? '34px Arial' : '28px Arial';
        
        // Draw rank in top-left
        ctx.font = rankFontSize;
        ctx.fillText(this.rankToSymbol(card.rank), x + textOffset, drawY + (isPlayerCard ? 24 : 20));
        
        // Draw suit in top-left (small)
        ctx.font = smallSuitFontSize;
        ctx.fillText(card.suit, x + textOffset, drawY + (isPlayerCard ? 48 : 40));
        
        // Draw large suit in center
        ctx.font = largeSuitFontSize;
        ctx.fillText(card.suit, x + width/2 - (isPlayerCard ? 10 : 8), drawY + height/2 + (isPlayerCard ? 12 : 10));
        
        // Draw rank in bottom-right (upside down)
        ctx.save();
        ctx.translate(x + width - textOffset, drawY + height - textOffset);
        ctx.rotate(Math.PI);
        ctx.font = rankFontSize;
        ctx.fillText(this.rankToSymbol(card.rank), 0, 0);
        ctx.restore();
        
        ctx.restore(); // Restore clip
        ctx.restore(); // Restore original context
        
        return {
            x: x,
            y: drawY,
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
            ctx.stroke();
            
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
    }
};

// Make cardRenderer available globally
if (typeof window !== 'undefined') {
    window.cardRenderer = cardRenderer;
}