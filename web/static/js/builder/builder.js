// Character Builder Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('characterBuilder', () => ({
        activePanel: null,
        selectedSlot: '',
        equippedItems: {},
        build: {},

        calculatedStats: {
            morale: 0,
            power: 0,
            armour: 0,
            might: 0,
            agility: 0,
            vitality: 0,
            will: 0,
            fate: 0,
            critical_rating: 0,
            finesse: 0,
            physical_mastery: 0,
            tactical_mastery: 0,
            outgoing_healing: 0,
            resistance: 0,
            critical_defence: 0,
            incoming_healing: 0,
            block: 0,
            parry: 0,
            evade: 0,
            physical_mitigation: 0,
            tactical_mitigation: 0
        },
        
        // EV Score tracking
        goalEv: 150.0,
        
        get buildEvScore() {
            let totalEv = 0;
            for (let slotType in this.build) {
                const equippedItem = this.build[slotType];
                if (equippedItem && equippedItem.item && equippedItem.item.ev) {
                    const evValue = parseFloat(equippedItem.item.ev);
                    if (!isNaN(evValue)) {
                        totalEv += evValue;
                    }
                }
            }
            return totalEv;
        },
        
        get buildEvDisplay() {
            return this.buildEvScore.toFixed(1);
        },
        
        get goalEvDisplay() {
            return this.goalEv.toFixed(1);
        },
        
        get buildScoreColor() {
            const score = this.buildEvScore;
            const goal = this.goalEv;
            
            if (score >= goal) {
                return 'text-green-400';
            } else if (score >= goal * 0.9) {
                return 'text-yellow-400';
            } else if (score >= goal * 0.7) {
                return 'text-orange-400';
            } else {
                return 'text-red-400';
            }
        },
        
        init() {
            console.log('Builder component initialized');
            
            window.addEventListener('item-selected', (event) => {
                this.handleItemSelection(event.detail);
            });
            
            window.addEventListener('close-panel', (event) => {
                this.closePanel(event.detail);
            });
            
            this.recalculateStats();
        },
        
        openPanel(panel) {
            this.activePanel = panel;
            document.body.style.overflow = 'hidden';
        },
        
        closePanel(panel) {
            if (this.activePanel === panel) {
                this.activePanel = null;
                document.body.style.overflow = '';
            }
        },
        
        openEquipmentSlot(slotType) {
            this.selectedSlot = slotType;
            this.loadItemsForSlot(slotType);
            this.openPanel('equipment');
        },
        
        async loadItemsForSlot(slotType) {
            const currentlyEquipped = this.build && this.build[slotType] ? this.build[slotType].item : null;
            
            window.dispatchEvent(new CustomEvent('load-slot-items', {
                detail: { 
                    slotType: slotType,
                    currentlyEquipped: currentlyEquipped
                }
            }));
        },
        
        handleItemSelection(selection) {
            if (selection.panelType === 'equipment') {
                const isValid = this.canItemBeEquippedInSlot(selection.item, selection.slot);
                if (!isValid) {
                    alert('Invalid selection: ' + selection.item.name + ' cannot be equipped in ' + selection.slot + ' slot.');
                    this.openEquipmentSlot(selection.slot);
                    return;
                }
            }
            
            if (!this.build) {
                this.build = {};
            }
            this.build[selection.slot] = {
                item: selection.item,
                concreteItem: selection.concreteItem
            };
            
            this.updateSlotDisplay(selection.slot, selection.item);
            this.recalculateStats();
        },
        
        updateSlotDisplay(slotType, item) {
            const slotElement = document.querySelector('[data-slot=\'' + slotType + '\']');
            if (slotElement) {
                const existingIcon = slotElement.querySelector('.item-icon');
                if (existingIcon) {
                    existingIcon.remove();
                }
                
                const iconContainer = document.createElement('div');
                iconContainer.className = 'item-icon w-full h-full relative rounded-lg overflow-hidden';
                
                if (item.icon_urls && item.icon_urls.length > 0) {
                    const reversedUrls = [...item.icon_urls].reverse();
                    
                    reversedUrls.forEach((url, i) => {
                        const img = document.createElement('img');
                        img.src = url;
                        img.alt = item.name + ' icon layer ' + (i + 1);
                        img.className = 'absolute inset-0 w-full h-full object-contain';
                        img.onerror = function() { this.style.display = 'none'; };
                        iconContainer.appendChild(img);
                    });
                } else {
                    const fallback = document.createElement('div');
                    fallback.className = 'w-full h-full bg-gray-700 rounded-lg flex items-center justify-center';
                    const dot = document.createElement('div');
                    dot.className = 'w-2 h-2 bg-green-500 rounded';
                    fallback.appendChild(dot);
                    iconContainer.appendChild(fallback);
                }
                
                slotElement.appendChild(iconContainer);
                slotElement.classList.remove('border', 'border-lotro-border', 'border-green-500');
                slotElement.classList.add('border-0');
                slotElement.title = item.name + ' (Level ' + item.base_ilvl + ')';
                slotElement.onclick = () => this.openEquipmentSlot(slotType);
            }
        },
        
        recalculateStats() {
            for (let statKey in this.calculatedStats) {
                this.calculatedStats[statKey] = 0;
            }
            
            for (let slotType in this.build) {
                const equippedItem = this.build[slotType];
                if (equippedItem && equippedItem.concreteItem && equippedItem.concreteItem.stat_values) {
                    if (Array.isArray(equippedItem.concreteItem.stat_values)) {
                        for (let stat of equippedItem.concreteItem.stat_values) {
                            if (stat && stat.stat_name && typeof stat.value === 'number') {
                                const statName = stat.stat_name.toLowerCase();
                                if (this.calculatedStats.hasOwnProperty(statName)) {
                                    this.calculatedStats[statName] += stat.value;
                                }
                            }
                        }
                    }
                }
            }
            
            this.updateStatsDisplay();
        },
        
        updateStatsDisplay() {
            const statMappings = [
                'morale', 'power', 'armour', 'might', 'agility', 'vitality', 'will', 'fate',
                'critical_rating', 'finesse', 'physical_mastery', 'tactical_mastery', 'outgoing_healing',
                'resistance', 'critical_defence', 'incoming_healing', 'block', 'parry', 'evade',
                'physical_mitigation', 'tactical_mitigation'
            ];
            
            statMappings.forEach(statKey => {
                this.updateStatDisplay(statKey, this.calculatedStats[statKey]);
            });
        },
        
        updateStatDisplay(statKey, value) {
            const statElement = document.querySelector('[data-stat=\'' + statKey + '\']');
            
            if (statElement) {
                const ratingSpan = statElement.querySelector('span:first-child');
                if (ratingSpan) {
                    ratingSpan.textContent = Math.floor(value).toLocaleString();
                } else {
                    statElement.textContent = Math.floor(value).toLocaleString();
                }
            }
        },
        

        
        canItemBeEquippedInSlot(item, builderSlot) {
            if (!item || !item.slot || !builderSlot) return false;
            
            const slotMapping = {
                'EAR': ['LEFT_EAR', 'RIGHT_EAR'],
                'LEFT_EAR': ['LEFT_EAR'],
                'RIGHT_EAR': ['RIGHT_EAR'],
                'NECK': ['NECK'],
                'WRIST': ['LEFT_WRIST', 'RIGHT_WRIST'],
                'LEFT_WRIST': ['LEFT_WRIST'],
                'RIGHT_WRIST': ['RIGHT_WRIST'],
                'FINGER': ['LEFT_FINGER', 'RIGHT_FINGER'],
                'LEFT_FINGER': ['LEFT_FINGER'],
                'RIGHT_FINGER': ['RIGHT_FINGER'],
                'POCKET': ['POCKET'],
                'HEAD': ['HEAD'],
                'SHOULDER': ['SHOULDERS'],
                'BACK': ['BACK'],
                'CHEST': ['CHEST'],
                'HAND': ['HANDS'],
                'LEGS': ['LEGS'],
                'FEET': ['FEET'],
                'EITHER_HAND': ['MAIN_HAND', 'OFF_HAND'],
                'MAIN_HAND': ['MAIN_HAND'],
                'OFF_HAND': ['OFF_HAND'],
                'RANGED_ITEM': ['RANGED'],
                'CLASS_SLOT': ['CLASS']
            };
            
            const compatibleSlots = slotMapping[item.slot] || [];
            return compatibleSlots.includes(builderSlot);
        }
    }));
}); 