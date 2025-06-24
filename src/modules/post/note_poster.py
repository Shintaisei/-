#!/usr/bin/env python3
"""
note投稿モジュール
noteへの記事投稿処理専用
記事作成から投稿まで管理
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from ..utils import InputUtils, ValidationUtils, TimeUtils

class NotePoster:
    def __init__(self, driver_manager, article_generator):
        """初期化"""
        self.driver_manager = driver_manager
        self.article_generator = article_generator
        self.driver = driver_manager.get_driver()
        self.wait = driver_manager.get_wait()

    def create_and_publish_article(self):
        """記事を作成・投稿"""
        try:
            print("📝 記事作成ページにアクセス中...")
            
            # Step 1: 投稿ボタンをクリック（メニューを開く）
            print("🎯 投稿ボタンをクリックしてメニューを開きます...")
            posting_selectors = [
                'button[aria-label="投稿"][aria-controls="postingMenu"]',
                'button[aria-label="投稿"]',
                '.o-navbarPrimary__postingButtonText'
            ]
            
            posting_button = None
            for selector in posting_selectors:
                try:
                    posting_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ 投稿ボタンを発見: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            
            # XPathでも試す
            if not posting_button:
                try:
                    posting_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "投稿")]')))
                    print("✅ 投稿ボタンを発見: XPath")
                except (TimeoutException, NoSuchElementException):
                    pass
            
            if not posting_button:
                print("投稿ボタンが見つからないため、直接記事作成ページにアクセスします...")
                self.driver.get("https://note.com/new")
                TimeUtils.random_delay(3, 5)
            else:
                # 投稿ボタンをクリック
                posting_button.click()
                print("📋 投稿メニューが表示されるまで待機中...")
                
                # メニューが開くまで待機（aria-expanded="true"になるまで）
                menu_opened = False
                try:
                    # 方法1: aria-expanded="true"を待機
                    self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="投稿"][aria-expanded="true"]')))
                    menu_opened = True
                    print("✅ 投稿メニューが開きました（aria-expanded確認）")
                except TimeoutException:
                    try:
                        # 方法2: メニューコンテナの存在を待機
                        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#postingMenu, [role="menu"], [aria-labelledby="postingMenu"]')))
                        menu_opened = True
                        print("✅ 投稿メニューが開きました（メニュー要素確認）")
                    except TimeoutException:
                        try:
                            # 方法3: JavaScript経由でメニューの可視性を確認
                            menu_visible = self.driver.execute_script("""
                                // メニューが表示されているかチェック
                                var menu = document.querySelector('#postingMenu') || 
                                          document.querySelector('[role="menu"]') ||
                                          document.querySelector('[aria-labelledby="postingMenu"]');
                                if (menu && menu.offsetHeight > 0) {
                                    return true;
                                }
                                
                                // リンク要素が表示されているかチェック
                                var links = document.querySelectorAll('a[href*="/new"]');
                                for (var i = 0; i < links.length; i++) {
                                    if (links[i].offsetHeight > 0 && 
                                        (links[i].textContent.includes('記事') || 
                                         links[i].textContent.includes('新しく'))) {
                                        return true;
                                    }
                                }
                                return false;
                            """)
                            
                            if menu_visible:
                                menu_opened = True
                                print("✅ 投稿メニューが開きました（JavaScript確認）")
                            else:
                                print("⚠️ メニューの表示状態を確認できませんが、続行します...")
                        except:
                            print("⚠️ メニューの開閉状態を確認できませんが、続行します...")
                
                # メニューが表示されるまで追加待機
                if menu_opened:
                    TimeUtils.random_delay(0.5, 1.0)  # メニューが完全に表示されるまで短時間待機
                else:
                    TimeUtils.random_delay(2, 3)  # メニュー状態不明な場合は長めに待機
                
                # Step 2: 投稿メニューから「新しく記事を書く」を選択
                print("📝 新しく記事を書くを選択中...")
                new_article_selectors = [
                    'a[href*="/new"]',
                    'a[href="/new"]',
                    '//a[contains(@href, "/new")]',
                    '//a[contains(text(), "新しく記事を書く")]',
                    '//a[contains(text(), "記事を書く")]',
                    '//a[contains(text(), "記事")]',
                    '#postingMenu a[href*="new"]',
                    '[aria-labelledby="postingMenu"] a[href*="new"]'
                ]
                
                new_article_link = None
                for selector in new_article_selectors:
                    try:
                        if selector.startswith('//'):
                            new_article_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            new_article_link = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        print(f"✅ 新しく記事を書くリンクを発見: {selector}")
                        break
                    except (TimeoutException, NoSuchElementException):
                        continue
                
                if new_article_link:
                    new_article_link.click()
                    print("🎯 新しく記事を書くをクリックしました")
                    TimeUtils.random_delay(3, 5)
                else:
                    print("⚠️ 新しく記事を書くリンクが見つからないため、直接アクセスします...")
                    # JavaScript経由でメニュー内のリンクを探す
                    new_link = self.driver.execute_script("""
                        // メニュー内のリンクを探す
                        var links = document.querySelectorAll('a');
                        for (var i = 0; i < links.length; i++) {
                            var href = links[i].getAttribute('href');
                            var text = links[i].textContent || links[i].innerText;
                            if ((href && href.includes('/new')) || 
                                text.includes('記事') || 
                                text.includes('新しく')) {
                                return links[i];
                            }
                        }
                        return null;
                    """)
                    
                    if new_link:
                        new_link.click()
                        print("✅ JavaScript経由で記事作成リンクをクリックしました")
                        TimeUtils.random_delay(3, 5)
                    else:
                        print("🔄 直接記事作成ページにアクセスします...")
                        self.driver.get("https://note.com/new")
                        TimeUtils.random_delay(3, 5)

            # 記事内容を生成
            article = self.article_generator.generate_article()
            title = article['title']
            content = article['content']
            print(f"📄 記事タイトル: {title}")

            # ページの読み込み完了を待つ
            print("⏳ ページの読み込み完了を待機中...")
            try:
                # エディターが読み込まれるまで待機
                self.wait.until(EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[placeholder*="タイトル"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.ProseMirror')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="タイトル"]'))
                ))
            except TimeoutException:
                print("エディターの読み込みに時間がかかっています。続行します...")

            # Step 3: タイトル入力
            print("✏️ タイトルを入力中...")
            title_selectors = [
                'textarea[placeholder*="タイトル"]',
                'input[placeholder*="タイトル"]',
                'textarea[placeholder="記事タイトル"]',
                'input[placeholder="記事タイトル"]',
                'textarea.title',
                '#title',
                '[data-testid="title-input"]'
            ]
            
            title_element = None
            for selector in title_selectors:
                try:
                    title_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"✅ タイトル入力フィールドを発見: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not title_element:
                # JavaScript経由でタイトル要素を探す
                print("標準セレクタでタイトルフィールドが見つからないため、JavaScript経由で探します...")
                title_element = self.driver.execute_script("""
                    // 様々な方法でタイトル入力フィールドを探す
                    var titleInputs = [
                        document.querySelector('textarea[placeholder*="タイトル"]'),
                        document.querySelector('input[placeholder*="タイトル"]'),
                        document.querySelector('textarea'),
                        document.querySelector('input[type="text"]'),
                        document.querySelector('[contenteditable="true"]')
                    ];
                    
                    for (var i = 0; i < titleInputs.length; i++) {
                        if (titleInputs[i] && titleInputs[i].offsetHeight > 0) {
                            return titleInputs[i];
                        }
                    }
                    return null;
                """)
                
                if not title_element:
                    raise Exception("タイトル入力フィールドが見つかりません")
            
            # タイトル要素の詳細情報を表示
            element_info = self.driver.execute_script("""
                var element = arguments[0];
                return {
                    tagName: element.tagName,
                    placeholder: element.placeholder || '',
                    value: element.value || '',
                    textContent: element.textContent || '',
                    contentEditable: element.contentEditable || '',
                    className: element.className || '',
                    id: element.id || ''
                };
            """, title_element)
            
            print(f"📋 タイトル要素情報:")
            print(f"   - タグ名: {element_info['tagName']}")
            print(f"   - プレースホルダー: {element_info['placeholder']}")
            print(f"   - 現在の値: '{element_info['value']}'")
            print(f"   - テキストコンテンツ: '{element_info['textContent']}'")
            print(f"   - contentEditable: {element_info['contentEditable']}")
            print(f"   - クラス名: {element_info['className']}")
            print(f"   - ID: {element_info['id']}")

            # タイトル入力（3回まで試行）
            title_input_success = False
            for attempt in range(3):
                print(f"📝 タイトル入力試行 {attempt + 1}/3")
                
                try:
                    # フィールドにフォーカス
                    title_element.click()
                    time.sleep(0.3)
                    
                    # 既存のテキストをクリア（確実な方法）
                    title_element.send_keys(Keys.CONTROL + "a")  # 全選択
                    time.sleep(0.1)
                    title_element.send_keys(Keys.DELETE)  # 削除
                    time.sleep(0.1)
                    
                    # タイトルを確実に入力
                    element_tag = title_element.tag_name.lower()
                    print(f"タイトル要素タイプ: {element_tag}")
                    
                    if element_tag == 'textarea':
                        # textareaの場合はJavaScript経由で確実に設定
                        self.driver.execute_script("""
                            arguments[0].value = arguments[1];
                            arguments[0].focus();
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        """, title_element, title)
                        
                        # タイトル入力後にEnterキーを押して確定
                        time.sleep(0.2)
                        title_element.send_keys(Keys.ENTER)
                        print("📝 タイトル確定のためEnterキーを押しました")
                        time.sleep(0.3)
                        
                    else:
                        # その他の要素の場合
                        InputUtils.paste_text(self.driver, title_element, title)
                        # Enterキーで確定
                        time.sleep(0.2)
                        title_element.send_keys(Keys.ENTER)
                        print("📝 タイトル確定のためEnterキーを押しました")
                        time.sleep(0.3)
                    
                    time.sleep(0.5)
                    
                    # 入力確認（より詳細に）
                    actual_value = self.driver.execute_script("""
                        var element = arguments[0];
                        return element.value || element.textContent || element.innerText || '';
                    """, title_element)
                    
                    print(f"入力後のタイトル値: '{actual_value}'")
                    print(f"期待されるタイトル: '{title}'")
                    
                    if actual_value and title in actual_value:
                        print(f"✅ タイトル入力成功: {actual_value}")
                        title_input_success = True
                        break
                    else:
                        print(f"⚠️ タイトル入力試行 {attempt + 1} が失敗、再試行します...")
                        print(f"   実際の値: '{actual_value}'")
                        print(f"   期待する値: '{title}'")
                        
                        # 失敗した場合は別の方法を試す
                        if attempt < 2:  # 最後の試行でない場合
                            print("🔄 別の入力方法を試行します...")
                            try:
                                # 方法2: 文字ごとに入力
                                title_element.clear()
                                time.sleep(0.2)
                                for char in title:
                                    title_element.send_keys(char)
                                    time.sleep(0.01)
                                
                                # 再確認
                                actual_value2 = self.driver.execute_script("""
                                    var element = arguments[0];
                                    return element.value || element.textContent || element.innerText || '';
                                """, title_element)
                                
                                if actual_value2 and title in actual_value2:
                                    print(f"✅ 文字ごと入力で成功: {actual_value2}")
                                    title_input_success = True
                                    break
                            except Exception as e2:
                                print(f"文字ごと入力も失敗: {e2}")
                        
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"❌ タイトル入力試行 {attempt + 1} でエラー: {e}")
                    time.sleep(1)
            
            if not title_input_success:
                raise Exception("タイトル入力に3回失敗しました")

            # タイトル入力後の最終確認（フォーカス移動後）
            print("🔍 タイトル入力の最終確認中...")
            time.sleep(0.5)
            
            final_title_value = self.driver.execute_script("""
                var element = arguments[0];
                return element.value || element.textContent || element.innerText || '';
            """, title_element)
            
            print(f"最終確認 - タイトル値: '{final_title_value}'")
            
            if not final_title_value or title not in final_title_value:
                print("⚠️ タイトルが消失している可能性があります。再入力を試行...")
                # 再度タイトルを入力
                title_element.click()
                time.sleep(0.2)
                title_element.send_keys(Keys.CONTROL + "a")
                time.sleep(0.1)
                title_element.send_keys(title)
                time.sleep(0.2)
                title_element.send_keys(Keys.ENTER)
                print("📝 タイトル再入力とEnter確定完了")
                time.sleep(0.5)
            else:
                print("✅ タイトルが正常に保持されています")
            
            TimeUtils.random_delay(0.2, 0.5)

            # Step 4: 本文入力
            print("📝 本文を入力中...")
            content_selectors = [
                '.ProseMirror',
                'div[contenteditable="true"]',
                'textarea[placeholder*="本文"]',
                '.editor-content',
                '#content',
                '[data-testid="editor"]'
            ]
            
            content_element = None
            for selector in content_selectors:
                try:
                    content_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"✅ 本文入力フィールドを発見: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not content_element:
                # JavaScript経由で本文要素を探す
                print("標準セレクタで本文フィールドが見つからないため、JavaScript経由で探します...")
                content_element = self.driver.execute_script("""
                    // 様々な方法で本文入力フィールドを探す
                    var contentInputs = [
                        document.querySelector('.ProseMirror'),
                        document.querySelector('div[contenteditable="true"]'),
                        document.querySelector('textarea'),
                        document.querySelector('[role="textbox"]')
                    ];
                    
                    for (var i = 0; i < contentInputs.length; i++) {
                        if (contentInputs[i] && contentInputs[i].offsetHeight > 0) {
                            return contentInputs[i];
                        }
                    }
                    return null;
                """)
                
                if not content_element:
                    raise Exception("本文入力フィールドが見つかりません")
            
            # 本文入力（3回まで試行）
            content_input_success = False
            for attempt in range(3):
                print(f"📝 本文入力試行 {attempt + 1}/3")
                
                try:
                    content_element.click()
                    time.sleep(0.3)
                    
                    # 既存のテキストをクリア
                    content_element.send_keys(Keys.CONTROL + "a")
                    time.sleep(0.1)
                    content_element.send_keys(Keys.DELETE)
                    time.sleep(0.1)
                    
                    element_tag = content_element.tag_name.lower()
                    is_contenteditable = content_element.get_attribute('contenteditable') == 'true'
                    print(f"本文要素タイプ: {element_tag}, contenteditable: {is_contenteditable}")
                    
                    if is_contenteditable:
                        # contenteditable要素の場合はJavaScript経由
                        self.driver.execute_script("""
                            var element = arguments[0];
                            var text = arguments[1];
                            element.innerHTML = text.replace(/\\n/g, '<br>');
                            element.focus();
                            element.dispatchEvent(new Event('input', { bubbles: true }));
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                        """, content_element, content)
                    elif element_tag == 'textarea':
                        # textareaの場合
                        self.driver.execute_script("""
                            arguments[0].value = arguments[1];
                            arguments[0].focus();
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        """, content_element, content)
                    else:
                        # その他の場合は通常の入力
                        content_element.send_keys(content)
                    
                    time.sleep(0.5)
                    
                    # 入力確認（より詳細に）
                    actual_value = self.driver.execute_script("""
                        var element = arguments[0];
                        return element.value || element.textContent || element.innerText || '';
                    """, content_element)
                    
                    print(f"入力後の本文値（最初の100文字）: '{actual_value[:100] if actual_value else 'なし'}...'")
                    
                    # 本文の最初の100文字で確認（改行を考慮）
                    expected_start = content[:100]
                    
                    # 改行を正規化して比較
                    normalized_actual = actual_value.replace('\n', '').replace('\r', '') if actual_value else ''
                    normalized_expected = expected_start.replace('\n', '').replace('\r', '')
                    
                    if normalized_actual and normalized_expected in normalized_actual:
                        print(f"✅ 本文入力成功（改行正規化後で確認）")
                        content_input_success = True
                        break
                    else:
                        print(f"⚠️ 本文入力試行 {attempt + 1} が失敗、再試行します...")
                        print(f"   期待する開始部分（正規化）: '{normalized_expected}'")
                        print(f"   実際の開始部分（正規化）: '{normalized_actual[:100] if normalized_actual else 'なし'}'")
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"❌ 本文入力試行 {attempt + 1} でエラー: {e}")
                    time.sleep(1)
            
            if not content_input_success:
                # 最後にもう一度確認
                final_value = self.driver.execute_script("""
                    var element = arguments[0];
                    return element.value || element.textContent || element.innerText || '';
                """, content_element)
                print(f"最終確認 - 本文フィールドの値（最初の100文字）: '{final_value[:100] if final_value else 'なし'}...'")
                
                expected_start = content[:100]
                
                # 改行を正規化して比較
                normalized_final = final_value.replace('\n', '').replace('\r', '') if final_value else ''
                normalized_expected = expected_start.replace('\n', '').replace('\r', '')
                
                if not normalized_final or normalized_expected not in normalized_final:
                    raise Exception(f"本文入力に3回失敗しました。最終値の開始部分（正規化）: '{normalized_final[:100] if normalized_final else 'なし'}'")
                else:
                    print("✅ 最終確認で本文入力が確認できました（改行正規化後）")
                    content_input_success = True

            TimeUtils.random_delay(0.2, 0.5)
            
            # 記事の入力完了後、下書き状態になるまで待機
            print("📝 記事の下書き保存を待機中...")
            TimeUtils.random_delay(3, 5)
            
            # ページの状態を確認
            page_info = self.driver.execute_script("""
                return {
                    url: window.location.href,
                    title: document.title,
                    hasEditor: !!document.querySelector('.ProseMirror'),
                    hasPublishButton: !!document.querySelector('button[data-type="primary"]'),
                    allButtons: Array.from(document.querySelectorAll('button')).map(btn => ({
                        text: btn.textContent || btn.innerText || '',
                        dataType: btn.getAttribute('data-type') || '',
                        ariaLabel: btn.getAttribute('aria-label') || ''
                    }))
                };
            """)
            
            print(f"📋 現在のページ状態:")
            print(f"  URL: {page_info['url']}")
            print(f"  タイトル: {page_info['title']}")
            print(f"  エディター存在: {page_info['hasEditor']}")
            print(f"  公開ボタン存在: {page_info['hasPublishButton']}")
            print(f"  表示されているボタン数: {len(page_info['allButtons'])}")
            
            # 表示されているボタンの詳細を出力
            for i, btn in enumerate(page_info['allButtons']):
                print(f"    ボタン{i+1}: '{btn['text']}' (data-type: {btn['dataType']})")

            # Step 5: 公開ボタンを探してクリック（下書き状態から公開設定へ）
            print("🚀 公開ボタンをクリック中...")
            
            # まず少し待機してページが安定するのを待つ
            TimeUtils.random_delay(2, 3)
            
            # 複数の方法で公開ボタンを探す
            publish_button = None
            
            # 方法1: 標準的なセレクタで探す（元のコードを完全再現）
            publish_selectors = [
                'button[data-type="primary"]',
                '.a-button[data-type="primary"]',
                'button.a-button[data-type="primary"]',
                '//button[contains(@class, "a-button") and contains(text(), "公開")]',
                '//button[contains(text(), "公開")]',
                '//button[@data-type="primary"]'
            ]
            
            for selector in publish_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        # ボタンが表示されていて、テキストに「公開」が含まれているかチェック
                        if element.is_displayed() and element.is_enabled():
                            button_text = element.text or element.get_attribute('textContent') or ''
                            if '公開' in button_text or element.get_attribute('data-type') == 'primary':
                                publish_button = element
                                print(f"✅ 公開ボタンを発見: {selector}, テキスト: '{button_text}'")
                                break
                    
                    if publish_button:
                        break
                        
                except Exception as e:
                    print(f"セレクタ {selector} でエラー: {e}")
                    continue
            
            # 方法2: JavaScript経由で詳細に探す（元のコードを完全再現）
            if not publish_button:
                print("標準セレクタで見つからないため、JavaScript経由で探します...")
                publish_button = self.driver.execute_script("""
                    // すべてのボタンを調べる
                    var buttons = document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        var btn = buttons[i];
                        var text = btn.textContent || btn.innerText || '';
                        var dataType = btn.getAttribute('data-type');
                        
                        // 表示されているボタンのみチェック
                        if (btn.offsetHeight > 0 && btn.offsetWidth > 0) {
                            // 公開関連のテキストまたはprimaryタイプをチェック
                            if (text.includes('公開') || text.includes('投稿') || text.includes('送信') ||
                                (dataType === 'primary' && !text.includes('ログイン') && !text.includes('登録') && !text.includes('キャンセル'))) {
                                console.log('公開ボタン候補:', text, 'data-type:', dataType);
                                return btn;
                            }
                        }
                    }
                    
                    // 見つからない場合はprimaryタイプのボタンを返す
                    var primaryBtns = document.querySelectorAll('button[data-type="primary"]');
                    for (var j = 0; j < primaryBtns.length; j++) {
                        if (primaryBtns[j].offsetHeight > 0) {
                            console.log('Primary ボタンを使用:', primaryBtns[j].textContent);
                            return primaryBtns[j];
                        }
                    }
                    
                    return null;
                """)
                
                if publish_button:
                    button_text = publish_button.text or publish_button.get_attribute('textContent') or ''
                    print(f"✅ JavaScript経由で公開ボタンを発見: '{button_text}'")
            
            if not publish_button:
                print("❌ 公開ボタンが見つかりません。現在のページ情報を確認します...")
                print(f"現在のURL: {self.driver.current_url}")
                
                # ページ上のすべてのボタンを表示
                all_buttons = self.driver.execute_script("""
                    var buttons = document.querySelectorAll('button');
                    var buttonInfo = [];
                    for (var i = 0; i < buttons.length; i++) {
                        var btn = buttons[i];
                        if (btn.offsetHeight > 0) {
                            buttonInfo.push({
                                text: btn.textContent || btn.innerText || '',
                                ariaLabel: btn.getAttribute('aria-label'),
                                dataType: btn.getAttribute('data-type'),
                                className: btn.className
                            });
                        }
                    }
                    return buttonInfo;
                """)
                
                print("現在ページの表示されているボタン一覧:")
                for i, btn_info in enumerate(all_buttons):
                    print(f"  {i+1}. テキスト: '{btn_info['text']}', aria-label: {btn_info['ariaLabel']}, data-type: {btn_info['dataType']}")
                
                raise Exception("公開ボタンが見つかりません")
            
            # 公開ボタンクリック前の確認（元のコードを完全再現）
            if ValidationUtils.confirm_before_click(publish_button, "公開"):
                # JavaScriptでクリック（より確実）
                self.driver.execute_script("arguments[0].click();", publish_button)
                print("🚀 公開ボタンをクリックしました")
            else:
                raise Exception("公開ボタンがクリックできない状態です")
            
            # 公開設定ページの読み込みを待つ
            TimeUtils.random_delay(2, 4)
            
            # Step 6: 最終投稿ボタンをクリック（元のコードを完全再現）
            print("🎯 最終投稿ボタンをクリック中...")
            
            # 最終投稿ボタンを探す
            final_button = None
            
            # 方法1: 標準的なセレクタで探す（元のコードを完全再現）
            final_publish_selectors = [
                'button[aria-label="投稿"]',
                'button[data-type="primary"]',
                '.a-button[data-type="primary"]',
                'button.a-button[data-type="primary"]',
                '//button[contains(text(), "投稿")]',
                '//button[contains(text(), "公開")]',
                '//button[@aria-label="投稿"]',
                '//button[@data-type="primary"]'
            ]
            
            for selector in final_publish_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            button_text = element.text or element.get_attribute('textContent') or ''
                            aria_label = element.get_attribute('aria-label') or ''
                            
                            # 投稿関連のテキストまたはaria-labelをチェック
                            if ('投稿' in button_text or '投稿' in aria_label or 
                                '公開' in button_text or element.get_attribute('data-type') == 'primary'):
                                final_button = element
                                print(f"✅ 最終投稿ボタンを発見: {selector}, テキスト: '{button_text}', aria-label: '{aria_label}'")
                                break
                    
                    if final_button:
                        break
                        
                except Exception as e:
                    print(f"セレクタ {selector} でエラー: {e}")
                    continue
            
            # 方法2: JavaScript経由で詳細に探す（元のコードを完全再現）
            if not final_button:
                print("標準セレクタで見つからないため、JavaScript経由で最終投稿ボタンを探します...")
                final_button = self.driver.execute_script("""
                    // すべてのボタンを調べる
                    var buttons = document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        var btn = buttons[i];
                        var text = btn.textContent || btn.innerText || '';
                        var ariaLabel = btn.getAttribute('aria-label') || '';
                        var dataType = btn.getAttribute('data-type');
                        
                        // 表示されているボタンのみチェック
                        if (btn.offsetHeight > 0 && btn.offsetWidth > 0) {
                            // 投稿関連のテキストをチェック
                            if (text.includes('投稿') || ariaLabel.includes('投稿') || 
                                text.includes('公開') || text.includes('送信') || text.includes('完了') ||
                                (dataType === 'primary' && !text.includes('ログイン') && !text.includes('登録') && !text.includes('キャンセル'))) {
                                console.log('最終投稿ボタン候補:', text, 'aria-label:', ariaLabel, 'data-type:', dataType);
                                return btn;
                            }
                        }
                    }
                    
                    return null;
                """)
                
                if final_button:
                    button_text = final_button.text or final_button.get_attribute('textContent') or ''
                    aria_label = final_button.get_attribute('aria-label') or ''
                    print(f"✅ JavaScript経由で最終投稿ボタンを発見: '{button_text}', aria-label: '{aria_label}'")
            
            if not final_button:
                print("❌ 最終投稿ボタンが見つかりません。現在のページ情報を確認します...")
                print(f"現在のURL: {self.driver.current_url}")
                
                # ページ上のすべてのボタンを表示
                all_buttons = self.driver.execute_script("""
                    var buttons = document.querySelectorAll('button');
                    var buttonInfo = [];
                    for (var i = 0; i < buttons.length; i++) {
                        var btn = buttons[i];
                        if (btn.offsetHeight > 0) {
                            buttonInfo.push({
                                text: btn.textContent || btn.innerText || '',
                                ariaLabel: btn.getAttribute('aria-label'),
                                dataType: btn.getAttribute('data-type'),
                                className: btn.className
                            });
                        }
                    }
                    return buttonInfo;
                """)
                
                print("現在ページの表示されているボタン一覧:")
                for i, btn_info in enumerate(all_buttons):
                    print(f"  {i+1}. テキスト: '{btn_info['text']}', aria-label: {btn_info['ariaLabel']}, data-type: {btn_info['dataType']}")
                
                raise Exception("最終投稿ボタンが見つかりません")
            
            # 最終投稿ボタンクリック前の確認（元のコードを完全再現）
            if ValidationUtils.confirm_before_click(final_button, "最終投稿"):
                # JavaScriptでクリック（より確実）
                self.driver.execute_script("arguments[0].click();", final_button)
                print("🎯 最終投稿ボタンをクリックしました")
            else:
                raise Exception("最終投稿ボタンがクリックできない状態です")
            
            # 投稿完了の確認（元のコードを完全再現）
            TimeUtils.random_delay(3, 5)
            
            # 投稿完了を確認
            try:
                # 投稿完了後のページ変遷を確認
                current_url = self.driver.current_url
                if '/n/' in current_url or 'note.com' in current_url:
                    print("🎉 記事の投稿が完了しました！")
                    print(f"投稿された記事URL: {current_url}")
                else:
                    print("⚠️ 投稿完了の確認ができませんが、処理は実行されました")
            except Exception as e:
                print(f"投稿完了確認中にエラー: {e}")

            return True
                
        except Exception as e:
            print(f"❌ 記事作成エラー: {e}")
            final_url = self.driver.current_url
            print(f"現在のURL: {final_url}")
            return False 