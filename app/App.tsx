import React, { useState, useEffect, useMemo } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  FlatList,
  SafeAreaView,
  StatusBar,
  ScrollView,
  Share,
  Platform,
  Alert,
  Image,
  Modal
} from 'react-native';
import * as Speech from 'expo-speech';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import dictionaryData from './assets/dictionary.json';

interface DictionaryEntry {
  id: number;
  category: string;
  english: string;
  japanese_kanji: string;
  japanese_kana: string;
  japanese_romaji: string;
  urdu_script: string;
  urdu_roman: string;
  example_en: string;
  example_ja: string;
  example_ur: string;
}

const CATEGORIES = ['All', 'Automotive', 'Software', 'Banking', 'Business', 'Workplace', 'Logistics', 'Medical', 'Legal', 'Bookmarks'];

export default function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [bookmarks, setBookmarks] = useState<number[]>([]);
  const [activeTab, setActiveTab] = useState<'dictionary' | 'flashcards'>('dictionary');
  const [flashcardIndex, setFlashcardIndex] = useState(0);
  const [isCardFlipped, setIsCardFlipped] = useState(false);
  const [speakingId, setSpeakingId] = useState<string | null>(null);
  const [aboutVisible, setAboutVisible] = useState(false);

  // Load Bookmarks on Mount
  useEffect(() => {
    (async () => {
      try {
        const saved = await AsyncStorage.getItem('@dictionary_bookmarks');
        if (saved) {
          setBookmarks(JSON.parse(saved));
        }
      } catch (e) {
        console.error('Failed to load bookmarks', e);
      }
    })();
  }, []);

  // Toggle Bookmark
  const toggleBookmark = async (id: number) => {
    const updated = bookmarks.includes(id)
      ? bookmarks.filter((bId) => bId !== id)
      : [...bookmarks, id];
    setBookmarks(updated);
    try {
      await AsyncStorage.setItem('@dictionary_bookmarks', JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to save bookmark', e);
    }
  };

  // Text-To-Speech with Audio Sanitization
  const speak = (text: string, lang: 'ja-JP' | 'en-US' | 'ur-PK', key: string) => {
    if (!text) return;

    // AUDIO SANITIZATION: Eliminate literal 'slash' pronunciation and unwanted symbols
    let cleaned = text;

    // 1. Take primary headword before slash to avoid engine saying 'slash' or 'スラッシュ'
    if (cleaned.includes('/')) {
      cleaned = cleaned.split('/')[0].trim();
    }

    // 2. Strip bracketed text and parenthesis acronyms (e.g. '(ATM)', '【注】')
    cleaned = cleaned.replace(/[（(][^）)]*[）)]/g, '').replace(/[【\[][^】\]]*[】\]]/g, '').trim();

    // 3. Language-specific cleanups
    if (lang === 'ja-JP') {
      // Remove any lingering Latin letters/digits from kana audio
      cleaned = cleaned.replace(/[a-zA-Z0-9_\-#@$%^&*]/g, '').trim();
      if (!cleaned) cleaned = text.split('/')[0].trim();
    } else if (lang === 'ur-PK') {
      // Remove any lingering Latin or Cyrillic characters
      cleaned = cleaned.replace(/[a-zA-Z\u0400-\u04FF]/g, '').trim();
      if (!cleaned) cleaned = text.split('/')[0].trim();
    } else if (lang === 'en-US') {
      cleaned = cleaned.replace(/[_/]/g, ' ').trim();
    }

    if (!cleaned) return;

    setSpeakingId(key);
    Speech.stop();
    Speech.speak(cleaned, {
      language: lang,
      rate: 0.9,
      onDone: () => setSpeakingId(null),
      onError: () => setSpeakingId(null),
    });
  };

  // Share Entry
  const shareEntry = async (entry: DictionaryEntry) => {
    try {
      await Share.share({
        message: `📘 ${entry.english}\n🇯🇵 ${entry.japanese_kanji} (${entry.japanese_romaji})\n🇵🇰 ${entry.urdu_script} (${entry.urdu_roman})\n\n💡 Example:\n${entry.example_en}\n${entry.example_ja}\n${entry.example_ur}`,
      });
    } catch (error) {
      console.error(error);
    }
  };

  // Filtered Dictionary List
  const filteredData = useMemo(() => {
    return (dictionaryData as DictionaryEntry[]).filter((item) => {
      const matchesCategory =
        selectedCategory === 'All'
          ? true
          : selectedCategory === 'Bookmarks'
          ? bookmarks.includes(item.id)
          : item.category.toLowerCase() === selectedCategory.toLowerCase();

      if (!matchesCategory) return false;

      if (!searchQuery.trim()) return true;

      const q = searchQuery.toLowerCase().trim();
      return (
        item.english.toLowerCase().includes(q) ||
        item.japanese_kanji.toLowerCase().includes(q) ||
        item.japanese_kana.toLowerCase().includes(q) ||
        item.japanese_romaji.toLowerCase().includes(q) ||
        item.urdu_script.includes(q) ||
        item.urdu_roman.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q)
      );
    });
  }, [searchQuery, selectedCategory, bookmarks]);

  // Flashcards List
  const flashcardList = useMemo(() => {
    return filteredData.length > 0 ? filteredData : (dictionaryData as DictionaryEntry[]);
  }, [filteredData]);

  const currentFlashcard = flashcardList[flashcardIndex] || flashcardList[0];

  const handleNextCard = () => {
    setIsCardFlipped(false);
    setFlashcardIndex((prev) => (prev + 1) % flashcardList.length);
  };

  const handlePrevCard = () => {
    setIsCardFlipped(false);
    setFlashcardIndex((prev) => (prev - 1 + flashcardList.length) % flashcardList.length);
  };

  const getCategoryIcon = (cat: string) => {
    switch (cat) {
      case 'Automotive':
        return 'car-sport-outline';
      case 'Software':
        return 'code-slash-outline';
      case 'Banking':
        return 'card-outline';
      case 'Business':
        return 'briefcase-outline';
      case 'Workplace':
        return 'people-outline';
      case 'Logistics':
        return 'boat-outline';
      case 'Medical':
        return 'medkit-outline';
      case 'Legal':
        return 'shield-checkmark-outline';
      case 'Bookmarks':
        return 'bookmark-outline';
      default:
        return 'apps-outline';
    }
  };

  const renderCard = ({ item }: { item: DictionaryEntry }) => {
    const isBookmarked = bookmarks.includes(item.id);

    return (
      <View style={styles.card}>
        {/* Card Header */}
        <View style={styles.cardHeader}>
          <View style={styles.categoryBadge}>
            <Ionicons name={getCategoryIcon(item.category)} size={13} color="#38BDF8" />
            <Text style={styles.categoryBadgeText}>{item.category}</Text>
          </View>
          <View style={styles.cardActions}>
            <TouchableOpacity
              onPress={() => speak(item.english, 'en-US', `en-${item.id}`)}
              style={styles.iconBtn}
            >
              <Ionicons
                name={speakingId === `en-${item.id}` ? 'volume-high' : 'volume-medium-outline'}
                size={18}
                color="#94A3B8"
              />
            </TouchableOpacity>
            <TouchableOpacity onPress={() => shareEntry(item)} style={styles.iconBtn}>
              <Ionicons name="share-social-outline" size={17} color="#94A3B8" />
            </TouchableOpacity>
            <TouchableOpacity onPress={() => toggleBookmark(item.id)} style={styles.iconBtn}>
              <Ionicons
                name={isBookmarked ? 'bookmark' : 'bookmark-outline'}
                size={18}
                color={isBookmarked ? '#F59E0B' : '#94A3B8'}
              />
            </TouchableOpacity>
          </View>
        </View>

        {/* English Term */}
        <Text style={styles.englishTerm}>{item.english}</Text>

        <View style={styles.divider} />

        {/* Japanese Section */}
        <View style={styles.langSection}>
          <View style={styles.langHeader}>
            <View style={styles.langPill}>
              <Text style={styles.langPillText}>日本語 • JAPANESE</Text>
            </View>
            <TouchableOpacity
              onPress={() => speak(item.japanese_kana || item.japanese_kanji, 'ja-JP', `ja-${item.id}`)}
              style={styles.soundButton}
            >
              <Ionicons
                name={speakingId === `ja-${item.id}` ? 'volume-high' : 'volume-medium-outline'}
                size={16}
                color="#0284C7"
              />
              <Text style={styles.soundButtonText}>Listen JP</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.japaneseKanji}>{item.japanese_kanji}</Text>
          <View style={styles.readingRow}>
            <Text style={styles.kanaText}>読み: {item.japanese_kana}</Text>
            <Text style={styles.romajiText}>[{item.japanese_romaji}]</Text>
          </View>
        </View>

        {/* Urdu Section */}
        <View style={styles.urduSection}>
          <View style={styles.langHeader}>
            <TouchableOpacity
              onPress={() => speak(item.urdu_script, 'ur-PK', `ur-${item.id}`)}
              style={styles.soundButtonUrdu}
            >
              <Ionicons
                name={speakingId === `ur-${item.id}` ? 'volume-high' : 'volume-medium-outline'}
                size={16}
                color="#059669"
              />
              <Text style={styles.soundButtonTextUrdu}>Listen UR</Text>
            </TouchableOpacity>
            <View style={styles.langPillUrdu}>
              <Text style={styles.langPillTextUrdu}>اردو • URDU</Text>
            </View>
          </View>
          <Text style={styles.urduScript}>{item.urdu_script}</Text>
          <Text style={styles.urduRoman}>Phonetics: {item.urdu_roman}</Text>
        </View>

        {/* Workplace Example Sentence Box */}
        {item.example_en ? (
          <View style={styles.exampleContainer}>
            <View style={styles.exampleHeader}>
              <Ionicons name="bulb-outline" size={14} color="#F59E0B" />
              <Text style={styles.exampleTitle}>Workplace Context</Text>
            </View>
            <Text style={styles.exampleEn}>• {item.example_en}</Text>
            <Text style={styles.exampleJa}>• {item.example_ja}</Text>
            <Text style={styles.exampleUr}>• {item.example_ur}</Text>
          </View>
        ) : null}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor="#0F172A" />

      {/* Main Header with Tech Reads Logo & Qualitex Trading LLC Branding */}
      <View style={styles.header}>
        <View style={styles.headerTitleRow}>
          <View style={styles.brandContainer}>
            <Image
              source={require('./assets/tech_reads_logo.jpg')}
              style={styles.headerLogo}
              resizeMode="cover"
            />
            <View style={styles.brandTextGroup}>
              <View style={styles.titleWithBadge}>
                <Text style={styles.appTitle}>TECH READS</Text>
                <View style={styles.langKanjiBadge}>
                  <Text style={styles.langKanjiBadgeText}>三語辞典</Text>
                </View>
              </View>
              <Text style={styles.appSubtitle}>Japanese 🇯🇵 • English 🇬🇧 • Urdu 🇵🇰</Text>
              <TouchableOpacity onPress={() => setAboutVisible(true)} style={styles.companyPill}>
                <Ionicons name="shield-checkmark" size={11} color="#38BDF8" style={{ marginRight: 4 }} />
                <Text style={styles.companyPillText}>Qualitex Trading LLC</Text>
                <Ionicons name="information-circle-outline" size={12} color="#94A3B8" style={{ marginLeft: 3 }} />
              </TouchableOpacity>
            </View>
          </View>
          <View style={styles.headerRightActions}>
            <View style={styles.badgeCount}>
              <Text style={styles.badgeCountText}>{filteredData.length} Terms</Text>
            </View>
          </View>
        </View>

        {/* Search Bar */}
        <View style={styles.searchBar}>
          <Ionicons name="search-outline" size={18} color="#94A3B8" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search English, 日本語, Romaji, or اردو..."
            placeholderTextColor="#64748B"
            value={searchQuery}
            onChangeText={setSearchQuery}
            clearButtonMode="while-editing"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Ionicons name="close-circle" size={18} color="#94A3B8" />
            </TouchableOpacity>
          )}
        </View>

        {/* Category Horizontal Filter */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoryScroll}
        >
          {CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <TouchableOpacity
                key={cat}
                onPress={() => setSelectedCategory(cat)}
                style={[styles.categoryChip, isSelected && styles.categoryChipActive]}
              >
                <Ionicons
                  name={getCategoryIcon(cat)}
                  size={14}
                  color={isSelected ? '#FFFFFF' : '#94A3B8'}
                  style={{ marginRight: 5 }}
                />
                <Text
                  style={[
                    styles.categoryChipText,
                    isSelected && styles.categoryChipTextActive,
                  ]}
                >
                  {cat}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        {/* Tab Switcher: Dictionary vs Flashcards */}
        <View style={styles.tabBar}>
          <TouchableOpacity
            style={[styles.tabBtn, activeTab === 'dictionary' && styles.tabBtnActive]}
            onPress={() => setActiveTab('dictionary')}
          >
            <Ionicons
              name="book-outline"
              size={16}
              color={activeTab === 'dictionary' ? '#38BDF8' : '#94A3B8'}
            />
            <Text
              style={[
                styles.tabText,
                activeTab === 'dictionary' && styles.tabTextActive,
              ]}
            >
              Dictionary List
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tabBtn, activeTab === 'flashcards' && styles.tabBtnActive]}
            onPress={() => {
              setActiveTab('flashcards');
              setIsCardFlipped(false);
            }}
          >
            <Ionicons
              name="school-outline"
              size={16}
              color={activeTab === 'flashcards' ? '#38BDF8' : '#94A3B8'}
            />
            <Text
              style={[
                styles.tabText,
                activeTab === 'flashcards' && styles.tabTextActive,
              ]}
            >
              Study Flashcards
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Content Area */}
      {activeTab === 'dictionary' ? (
        <FlatList
          data={filteredData}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderCard}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Ionicons name="search" size={42} color="#475569" />
              <Text style={styles.emptyTitle}>No matching terms found</Text>
              <Text style={styles.emptySubtitle}>Try searching in Romaji, Urdu script, or Kanji.</Text>
            </View>
          }
          ListFooterComponent={
            <View style={styles.listFooter}>
              <View style={styles.footerBrandRow}>
                <Image
                  source={require('./assets/tech_reads_logo.jpg')}
                  style={styles.footerLogo}
                  resizeMode="cover"
                />
                <View style={{ marginLeft: 12 }}>
                  <Text style={styles.footerBrandTitle}>TECH READS™</Text>
                  <Text style={styles.footerBrandSub}>三語プロフェッショナル辞典</Text>
                </View>
              </View>
              <View style={styles.footerDivider} />
              <TouchableOpacity onPress={() => setAboutVisible(true)} style={styles.footerCompanyBadge}>
                <Ionicons name="shield-checkmark" size={13} color="#38BDF8" style={{ marginRight: 6 }} />
                <Text style={styles.footerCompanyName}>Qualitex Trading LLC</Text>
              </TouchableOpacity>
              <Text style={styles.footerCopyrightText}>
                © {new Date().getFullYear()} Qualitex Trading LLC. All Rights Reserved.
              </Text>
              <Text style={styles.footerTagline}>
                Play • Learn • Innovate • Automotive • Software • Trade
              </Text>
            </View>
          }
        />
      ) : (
        /* Flashcards Mode */
        <View style={styles.flashcardContainer}>
          <View style={styles.flashcardHeader}>
            <Text style={styles.flashcardProgress}>
              Card {flashcardIndex + 1} of {flashcardList.length}
            </Text>
            <TouchableOpacity
              onPress={() => toggleBookmark(currentFlashcard.id)}
              style={styles.iconBtn}
            >
              <Ionicons
                name={bookmarks.includes(currentFlashcard.id) ? 'bookmark' : 'bookmark-outline'}
                size={22}
                color={bookmarks.includes(currentFlashcard.id) ? '#F59E0B' : '#94A3B8'}
              />
            </TouchableOpacity>
          </View>

          {/* Interactive Flip Card */}
          <TouchableOpacity
            activeOpacity={0.9}
            onPress={() => setIsCardFlipped(!isCardFlipped)}
            style={[styles.flashcardMain, isCardFlipped && styles.flashcardFlipped]}
          >
            <View style={styles.flashcardTopBadge}>
              <Text style={styles.flashcardBadgeText}>{currentFlashcard.category}</Text>
              <Text style={styles.tapFlipNotice}>
                {isCardFlipped ? 'Tap to see Front' : 'Tap to reveal Answer'}
              </Text>
            </View>

            {!isCardFlipped ? (
              /* Front of Card: English Term */
              <View style={styles.cardFrontContent}>
                <Ionicons name="globe-outline" size={32} color="#38BDF8" style={{ marginBottom: 12 }} />
                <Text style={styles.flashcardEnTerm}>{currentFlashcard.english}</Text>
                <Text style={styles.flashcardInstruction}>What is this in Japanese & Urdu?</Text>
                <TouchableOpacity
                  onPress={(e) => {
                    e.stopPropagation();
                    speak(currentFlashcard.english, 'en-US', 'fc-en');
                  }}
                  style={styles.fcSoundBtn}
                >
                  <Ionicons name="volume-medium" size={18} color="#38BDF8" />
                  <Text style={styles.fcSoundBtnText}>Pronounce English</Text>
                </TouchableOpacity>
              </View>
            ) : (
              /* Back of Card: Japanese & Urdu Solutions */
              <ScrollView showsVerticalScrollIndicator={false} style={styles.cardBackContent}>
                <Text style={styles.fcEnglishPrompt}>{currentFlashcard.english}</Text>

                <View style={styles.fcDivider} />

                {/* Japanese Answer */}
                <View style={styles.fcLangBlock}>
                  <View style={styles.fcLangRow}>
                    <Text style={styles.fcLangTag}>🇯🇵 Japanese</Text>
                    <TouchableOpacity
                      onPress={(e) => {
                        e.stopPropagation();
                        speak(currentFlashcard.japanese_kana, 'ja-JP', 'fc-ja');
                      }}
                      style={styles.miniSoundBtn}
                    >
                      <Ionicons name="volume-medium" size={16} color="#38BDF8" />
                    </TouchableOpacity>
                  </View>
                  <Text style={styles.fcKanji}>{currentFlashcard.japanese_kanji}</Text>
                  <Text style={styles.fcKana}>
                    {currentFlashcard.japanese_kana} • [{currentFlashcard.japanese_romaji}]
                  </Text>
                </View>

                {/* Urdu Answer */}
                <View style={styles.fcLangBlockUrdu}>
                  <View style={styles.fcLangRowUrdu}>
                    <TouchableOpacity
                      onPress={(e) => {
                        e.stopPropagation();
                        speak(currentFlashcard.urdu_script, 'ur-PK', 'fc-ur');
                      }}
                      style={styles.miniSoundBtnUrdu}
                    >
                      <Ionicons name="volume-medium" size={16} color="#10B981" />
                    </TouchableOpacity>
                    <Text style={styles.fcLangTagUrdu}>اردو • 🇵🇰</Text>
                  </View>
                  <Text style={styles.fcUrdu}>{currentFlashcard.urdu_script}</Text>
                  <Text style={styles.fcUrduRoman}>{currentFlashcard.urdu_roman}</Text>
                </View>

                {/* Example sentence */}
                {currentFlashcard.example_en ? (
                  <View style={styles.fcExampleBox}>
                    <Text style={styles.fcExEn}>• {currentFlashcard.example_en}</Text>
                    <Text style={styles.fcExJa}>• {currentFlashcard.example_ja}</Text>
                    <Text style={styles.fcExUr}>• {currentFlashcard.example_ur}</Text>
                  </View>
                ) : null}
              </ScrollView>
            )}
          </TouchableOpacity>

          {/* Controls: Prev / Next */}
          <View style={styles.flashcardControls}>
            <TouchableOpacity onPress={handlePrevCard} style={styles.fcNavBtn}>
              <Ionicons name="arrow-back" size={20} color="#F1F5F9" />
              <Text style={styles.fcNavBtnText}>Previous</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => {
                const randomIdx = Math.floor(Math.random() * flashcardList.length);
                setIsCardFlipped(false);
                setFlashcardIndex(randomIdx);
              }}
              style={styles.fcShuffleBtn}
            >
              <Ionicons name="shuffle" size={18} color="#94A3B8" />
            </TouchableOpacity>

            <TouchableOpacity onPress={handleNextCard} style={[styles.fcNavBtn, styles.fcNavBtnPrimary]}>
              <Text style={styles.fcNavBtnTextPrimary}>Next Card</Text>
              <Ionicons name="arrow-forward" size={20} color="#0F172A" />
            </TouchableOpacity>
          </View>

          {/* Flashcard Brand Footer */}
          <TouchableOpacity onPress={() => setAboutVisible(true)} style={styles.fcBrandFooter}>
            <Image
              source={require('./assets/tech_reads_logo.jpg')}
              style={styles.fcFooterLogo}
              resizeMode="cover"
            />
            <Text style={styles.fcFooterBrandText}>
              Tech Reads™ • © {new Date().getFullYear()} Qualitex Trading LLC
            </Text>
            <Ionicons name="information-circle-outline" size={13} color="#94A3B8" />
          </TouchableOpacity>
        </View>
      )}

      {/* About & Copyright Modal */}
      <Modal
        visible={aboutVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setAboutVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Image
              source={require('./assets/tech_reads_logo.jpg')}
              style={styles.modalLogo}
              resizeMode="cover"
            />
            <Text style={styles.modalTitle}>TECH READS™</Text>
            <Text style={styles.modalSubtitle}>三語辞典 • Professional Trilingual Technical Lexicon</Text>

            <View style={styles.modalBadgeRow}>
              <View style={styles.modalTag}>
                <Text style={styles.modalTagText}>Japanese 🇯🇵</Text>
              </View>
              <View style={styles.modalTag}>
                <Text style={styles.modalTagText}>English 🇬🇧</Text>
              </View>
              <View style={styles.modalTag}>
                <Text style={styles.modalTagText}>Urdu 🇵🇰</Text>
              </View>
            </View>

            <View style={styles.modalDivider} />

            <View style={styles.companyInfoBox}>
              <Image
                source={require('./assets/qualitex_logo.jpg')}
                style={styles.modalQtLogo}
                resizeMode="cover"
              />
              <View style={{ flex: 1, marginLeft: 12 }}>
                <Text style={styles.companyName}>QUALITEX TRADING LLC</Text>
                <Text style={styles.companyDesc}>
                  Specialized International Trade, Automotive Export & Cross-Border Enterprise Software Solutions.
                </Text>
              </View>
            </View>

            <View style={styles.copyrightBox}>
              <Text style={styles.copyrightText}>
                © {new Date().getFullYear()} Qualitex Trading LLC.
              </Text>
              <Text style={styles.copyrightSubtext}>
                All Intellectual Property, Trademarks, and Lexicographical Database contents are proprietary to Qualitex Trading LLC.
              </Text>
            </View>

            <TouchableOpacity
              onPress={() => setAboutVisible(false)}
              style={styles.closeModalBtn}
            >
              <Text style={styles.closeModalBtnText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  header: {
    paddingHorizontal: 16,
    paddingTop: Platform.OS === 'android' ? 36 : 12,
    paddingBottom: 10,
    backgroundColor: '#0F172A',
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
  },
  headerTitleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  brandContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 8,
  },
  headerLogo: {
    width: 46,
    height: 46,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: '#38BDF8',
    marginRight: 10,
  },
  brandTextGroup: {
    flex: 1,
  },
  titleWithBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  appTitle: {
    fontSize: 18,
    fontWeight: '900',
    color: '#F8FAFC',
    letterSpacing: 0.8,
  },
  langKanjiBadge: {
    backgroundColor: 'rgba(56, 189, 248, 0.15)',
    paddingHorizontal: 6,
    paddingVertical: 1.5,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#38BDF8',
  },
  langKanjiBadgeText: {
    color: '#38BDF8',
    fontSize: 10,
    fontWeight: '700',
  },
  appSubtitle: {
    fontSize: 11,
    color: '#94A3B8',
    marginTop: 1,
    fontWeight: '500',
  },
  companyPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(30, 41, 59, 0.9)',
    alignSelf: 'flex-start',
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderRadius: 6,
    marginTop: 3,
    borderWidth: 1,
    borderColor: '#334155',
  },
  companyPillText: {
    color: '#38BDF8',
    fontSize: 10,
    fontWeight: '700',
  },
  headerRightActions: {
    alignItems: 'flex-end',
  },
  badgeCount: {
    backgroundColor: '#1E293B',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#334155',
  },
  badgeCountText: {
    color: '#38BDF8',
    fontSize: 12,
    fontWeight: '700',
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1E293B',
    borderRadius: 12,
    paddingHorizontal: 12,
    height: 44,
    borderWidth: 1,
    borderColor: '#334155',
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    color: '#F8FAFC',
    fontSize: 14,
    height: '100%',
  },
  categoryScroll: {
    paddingVertical: 10,
    gap: 8,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1E293B',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#334155',
    marginRight: 8,
  },
  categoryChipActive: {
    backgroundColor: '#0284C7',
    borderColor: '#38BDF8',
  },
  categoryChipText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#94A3B8',
  },
  categoryChipTextActive: {
    color: '#FFFFFF',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#1E293B',
    borderRadius: 10,
    padding: 3,
    marginTop: 4,
  },
  tabBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    borderRadius: 8,
    gap: 6,
  },
  tabBtnActive: {
    backgroundColor: '#0F172A',
  },
  tabText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#94A3B8',
  },
  tabTextActive: {
    color: '#38BDF8',
  },
  listContent: {
    padding: 16,
    gap: 14,
  },
  card: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#334155',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(56, 189, 248, 0.12)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    gap: 4,
  },
  categoryBadgeText: {
    color: '#38BDF8',
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  cardActions: {
    flexDirection: 'row',
    gap: 8,
  },
  iconBtn: {
    padding: 4,
  },
  englishTerm: {
    fontSize: 20,
    fontWeight: '700',
    color: '#F8FAFC',
    letterSpacing: 0.2,
  },
  divider: {
    height: 1,
    backgroundColor: '#334155',
    marginVertical: 12,
  },
  langSection: {
    marginBottom: 12,
  },
  langHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  langPill: {
    backgroundColor: 'rgba(56, 189, 248, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  langPillText: {
    color: '#38BDF8',
    fontSize: 10,
    fontWeight: '700',
  },
  soundButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F172A',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#334155',
    gap: 4,
  },
  soundButtonText: {
    color: '#94A3B8',
    fontSize: 11,
    fontWeight: '600',
  },
  japaneseKanji: {
    fontSize: 22,
    fontWeight: '800',
    color: '#E2E8F0',
    marginBottom: 4,
  },
  readingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  kanaText: {
    fontSize: 14,
    color: '#38BDF8',
    fontWeight: '600',
  },
  romajiText: {
    fontSize: 13,
    color: '#94A3B8',
    fontStyle: 'italic',
  },
  urduSection: {
    marginTop: 4,
    marginBottom: 10,
  },
  langPillUrdu: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  langPillTextUrdu: {
    color: '#10B981',
    fontSize: 10,
    fontWeight: '700',
  },
  soundButtonUrdu: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F172A',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#334155',
    gap: 4,
  },
  soundButtonTextUrdu: {
    color: '#94A3B8',
    fontSize: 11,
    fontWeight: '600',
  },
  urduScript: {
    fontSize: 24,
    fontWeight: '700',
    color: '#10B981',
    textAlign: 'right',
    marginTop: 4,
    marginBottom: 4,
    lineHeight: 36,
  },
  urduRoman: {
    fontSize: 13,
    color: '#A7F3D0',
    textAlign: 'right',
    fontStyle: 'italic',
  },
  exampleContainer: {
    backgroundColor: '#0F172A',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#334155',
    marginTop: 4,
  },
  exampleHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 6,
  },
  exampleTitle: {
    color: '#F59E0B',
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  exampleEn: {
    fontSize: 12,
    color: '#CBD5E1',
    marginBottom: 4,
    lineHeight: 18,
  },
  exampleJa: {
    fontSize: 12,
    color: '#93C5FD',
    marginBottom: 4,
    lineHeight: 18,
  },
  exampleUr: {
    fontSize: 13,
    color: '#A7F3D0',
    textAlign: 'right',
    lineHeight: 20,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#E2E8F0',
    marginTop: 12,
  },
  emptySubtitle: {
    fontSize: 13,
    color: '#64748B',
    marginTop: 4,
  },
  flashcardContainer: {
    flex: 1,
    padding: 16,
    justifyContent: 'space-between',
  },
  flashcardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  flashcardProgress: {
    fontSize: 13,
    fontWeight: '700',
    color: '#94A3B8',
  },
  flashcardMain: {
    backgroundColor: '#1E293B',
    borderRadius: 20,
    padding: 24,
    minHeight: 380,
    borderWidth: 1.5,
    borderColor: '#334155',
    justifyContent: 'space-between',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 6,
  },
  flashcardFlipped: {
    borderColor: '#0284C7',
  },
  flashcardTopBadge: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  flashcardBadgeText: {
    color: '#38BDF8',
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  tapFlipNotice: {
    color: '#64748B',
    fontSize: 11,
    fontWeight: '500',
  },
  cardFrontContent: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 50,
  },
  flashcardEnTerm: {
    fontSize: 28,
    fontWeight: '800',
    color: '#F8FAFC',
    textAlign: 'center',
    marginBottom: 8,
  },
  flashcardInstruction: {
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
    marginBottom: 24,
  },
  fcSoundBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F172A',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: '#334155',
    gap: 8,
  },
  fcSoundBtnText: {
    color: '#38BDF8',
    fontSize: 13,
    fontWeight: '600',
  },
  cardBackContent: {
    flex: 1,
    marginTop: 8,
  },
  fcEnglishPrompt: {
    fontSize: 18,
    fontWeight: '700',
    color: '#94A3B8',
    textAlign: 'center',
  },
  fcDivider: {
    height: 1,
    backgroundColor: '#334155',
    marginVertical: 12,
  },
  fcLangBlock: {
    backgroundColor: '#0F172A',
    padding: 12,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#334155',
  },
  fcLangRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  fcLangTag: {
    fontSize: 11,
    fontWeight: '700',
    color: '#38BDF8',
  },
  miniSoundBtn: {
    padding: 4,
  },
  fcKanji: {
    fontSize: 22,
    fontWeight: '800',
    color: '#F8FAFC',
  },
  fcKana: {
    fontSize: 13,
    color: '#94A3B8',
    marginTop: 2,
  },
  fcLangBlockUrdu: {
    backgroundColor: '#0F172A',
    padding: 12,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#334155',
  },
  fcLangRowUrdu: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  fcLangTagUrdu: {
    fontSize: 11,
    fontWeight: '700',
    color: '#10B981',
  },
  miniSoundBtnUrdu: {
    padding: 4,
  },
  fcUrdu: {
    fontSize: 24,
    fontWeight: '700',
    color: '#10B981',
    textAlign: 'right',
  },
  fcUrduRoman: {
    fontSize: 13,
    color: '#6EE7B7',
    textAlign: 'right',
    marginTop: 2,
    fontStyle: 'italic',
  },
  fcExampleBox: {
    backgroundColor: 'rgba(245, 158, 11, 0.08)',
    padding: 10,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#F59E0B',
  },
  fcExEn: {
    fontSize: 12,
    color: '#FDE68A',
    marginBottom: 4,
  },
  fcExJa: {
    fontSize: 12,
    color: '#93C5FD',
    marginBottom: 4,
  },
  fcExUr: {
    fontSize: 12,
    color: '#A7F3D0',
    textAlign: 'right',
  },
  flashcardControls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 16,
    gap: 12,
  },
  fcNavBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1E293B',
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
    gap: 6,
  },
  fcNavBtnPrimary: {
    backgroundColor: '#38BDF8',
    borderColor: '#38BDF8',
  },
  fcNavBtnText: {
    color: '#F1F5F9',
    fontSize: 14,
    fontWeight: '600',
  },
  fcNavBtnTextPrimary: {
    color: '#0F172A',
    fontSize: 14,
    fontWeight: '700',
  },
  fcShuffleBtn: {
    padding: 12,
    backgroundColor: '#1E293B',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  fcBrandFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    marginTop: 14,
    borderTopWidth: 1,
    borderTopColor: '#1E293B',
    gap: 8,
  },
  fcFooterLogo: {
    width: 20,
    height: 20,
    borderRadius: 5,
  },
  fcFooterBrandText: {
    color: '#64748B',
    fontSize: 11,
    fontWeight: '600',
  },
  listFooter: {
    alignItems: 'center',
    paddingVertical: 32,
    paddingHorizontal: 16,
    borderTopWidth: 1,
    borderTopColor: '#1E293B',
    marginTop: 24,
    backgroundColor: '#0B1120',
    borderRadius: 16,
    marginBottom: 40,
    borderWidth: 1,
    borderColor: '#1E293B',
  },
  footerBrandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  footerLogo: {
    width: 44,
    height: 44,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: '#38BDF8',
  },
  footerBrandTitle: {
    color: '#F8FAFC',
    fontSize: 15,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  footerBrandSub: {
    color: '#94A3B8',
    fontSize: 11,
    fontWeight: '500',
  },
  footerDivider: {
    width: 60,
    height: 2,
    backgroundColor: '#334155',
    marginVertical: 12,
    borderRadius: 1,
  },
  footerCompanyBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1E293B',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#334155',
    marginBottom: 10,
  },
  footerCompanyName: {
    color: '#E2E8F0',
    fontSize: 12,
    fontWeight: '700',
  },
  footerCopyrightText: {
    color: '#64748B',
    fontSize: 11,
    textAlign: 'center',
    marginBottom: 4,
    fontWeight: '500',
  },
  footerTagline: {
    color: '#475569',
    fontSize: 10,
    textAlign: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#1E293B',
    borderRadius: 20,
    padding: 24,
    width: '100%',
    maxWidth: 440,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#334155',
  },
  modalLogo: {
    width: 80,
    height: 80,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#38BDF8',
    marginBottom: 12,
  },
  modalTitle: {
    color: '#F8FAFC',
    fontSize: 22,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  modalSubtitle: {
    color: '#94A3B8',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 2,
    marginBottom: 14,
  },
  modalBadgeRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  modalTag: {
    backgroundColor: '#0F172A',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#334155',
  },
  modalTagText: {
    color: '#38BDF8',
    fontSize: 11,
    fontWeight: '600',
  },
  modalDivider: {
    width: '100%',
    height: 1,
    backgroundColor: '#334155',
    marginBottom: 16,
  },
  companyInfoBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F172A',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
    marginBottom: 14,
    width: '100%',
  },
  modalQtLogo: {
    width: 48,
    height: 48,
    borderRadius: 8,
  },
  companyName: {
    color: '#F8FAFC',
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 2,
  },
  companyDesc: {
    color: '#94A3B8',
    fontSize: 11,
    lineHeight: 15,
  },
  copyrightBox: {
    backgroundColor: 'rgba(56, 189, 248, 0.05)',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(56, 189, 248, 0.15)',
    marginBottom: 16,
    width: '100%',
  },
  copyrightText: {
    color: '#38BDF8',
    fontSize: 11,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 3,
  },
  copyrightSubtext: {
    color: '#64748B',
    fontSize: 10,
    textAlign: 'center',
    lineHeight: 14,
  },
  closeModalBtn: {
    backgroundColor: '#38BDF8',
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
  },
  closeModalBtnText: {
    color: '#0F172A',
    fontSize: 14,
    fontWeight: '700',
  },
});
