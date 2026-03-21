import responses

from django.test.testcases import SimpleTestCase

from mock import MagicMock, patch
from robber import expect

from data_importer.copa_crawler.portal_crawler import (
    OpenCopaInvestigationCrawler,
    BaseComplaintCrawler,
    ComplaintCrawler,
    VimeoSimpleAPI
)


class OpenCopaInvestigationCrawlerTest(SimpleTestCase):
    @patch('data_importer.copa_crawler.portal_crawler.requests')
    def test_parse(self, requests):
        html = '''
            <html>
              <body>
                <div class="search-filter-results">
                  <div class="table-responsive">
                    <table class="table table-striped display wrap" id="ipra-case-search-data-table">
                      <tbody>
                        <tr>
                          <th>
                            <a href="http://www.iprachicago.org/case/1063127-2/" rel="bookmark">1063127</a>
                          </th>
                        </tr>
                        <tr>
                          <th>
                            <a href="http://www.iprachicago.org/case/1063442-2/" rel="bookmark">1063442</a>
                          </th>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div class="pagination">
                    <div class="nav-previous"></div>
                    <div> Page 1 of 1</div>
                    <div class="nav-next"></div>
                  </div>
                </div>
              </body>
            </html>
        '''
        requests.get.return_value.text = html
        requests.get.return_value.raise_for_status = MagicMock()

        links = ['http://www.iprachicago.org/case/1063127-2/', 'http://www.iprachicago.org/case/1063442-2/']
        expect(OpenCopaInvestigationCrawler().crawl()).to.be.eq(links)

    @patch('data_importer.copa_crawler.portal_crawler.requests')
    def test_parse_multiple_pages(self, requests):
        first_page_html = '''
            <html>
              <body>
                <div class="search-filter-results">
                  <div class="table-responsive">
                    <table class="table table-striped display wrap" id="ipra-case-search-data-table">
                      <tbody>
                        <tr>
                          <th>
                            <a href="http://www.iprachicago.org/case/1111111-1/" rel="bookmark">1111111</a>
                          </th>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div class="pagination">
                    <div class="nav-previous"></div>
                    <div> Page 1 of 2</div>
                    <div class="nav-next">
                      <a href="https://www.chicagocopa.org/case-portal?sort_order=title+desc&sf_paged=2">Next</a>
                    </div>
                  </div>
                </div>
              </body>
            </html>
        '''

        second_page_html = '''
            <html>
              <body>
                <div class="search-filter-results">
                  <div class="table-responsive">
                    <table class="table table-striped display wrap" id="ipra-case-search-data-table">
                      <tbody>
                        <tr>
                          <th>
                            <a href="http://www.iprachicago.org/case/2222222-2/" rel="bookmark">2222222</a>
                          </th>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div class="pagination">
                    <div class="nav-previous"></div>
                    <div> Page 2 of 2</div>
                    <div class="nav-next"></div>
                  </div>
                </div>
              </body>
            </html>
        '''

        responses_sequence = [
            MagicMock(text=first_page_html, raise_for_status=MagicMock()),
            MagicMock(text=second_page_html, raise_for_status=MagicMock()),
        ]
        requests.get.side_effect = responses_sequence

        links = [
            'http://www.iprachicago.org/case/1111111-1/',
            'http://www.iprachicago.org/case/2222222-2/',
        ]
        expect(OpenCopaInvestigationCrawler().crawl()).to.be.eq(links)


class BaseComplaintCrawlerTest(SimpleTestCase):
    URL = 'http://www.iprachicago.org/case/1042532-2/'

    @patch('data_importer.copa_crawler.portal_crawler.requests')
    def test_get_html_content(self, requests):
        requests.get = MagicMock(return_value=MagicMock(text='something'))
        expect(BaseComplaintCrawler().get_html_content(self.URL)).to.be.eq('something')

    @patch('data_importer.copa_crawler.portal_crawler.requests')
    def test_parse(self, requests):
        requests.get = MagicMock(return_value=MagicMock(text='something'))

        class SampleBaseComplaintCrawler(BaseComplaintCrawler):
            def _parse_field_1(self):
                return 'key_1'

            def _parse_field_2(self):
                return 'key_2'

            def _not_parse_field(self):
                return 'key_n'

        expect(SampleBaseComplaintCrawler(url=self.URL).crawl()).to.be.eq({
            'field_1': 'key_1',
            'field_2': 'key_2'
        })


class ComplaintCrawlerTest(SimpleTestCase):
    URL = 'http://www.iprachicago.org/case/1042532-2/'
    HTML_CONTENT = '''
    <div class="entry-content">
        <div class="table-responsive hidden-sm hidden-xs">
            <table class="table table-striped">
                <thead>
                <tr>
                    <th scope="col">Log#</th>
                    <th scope="col">Incident Type(s)</th>
                    <th scope="col">IPRA/COPA Notification Date</th>
                    <th scope="col">Incident Date &amp; Time</th>
                    <th scope="col">District of Occurrence</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <th scope="row">
                        1061883
                    </th>
                    <td>
                        Firearm Discharge
                    </td>
                    <td>
                        04-30-2013
                    </td>
                    <td>
                        04-30-2013 9:30 pm
                    </td>
                    <td>
                        04
                    </td>
                </tr>
                </tbody>
            </table>
        </div>
        <div class="table-responsive hidden-xs hidden-md stack-table">
            <table>
            </table>
        </div>

        %s
        <time class="entry-date published" datetime="2018-10-30T15:00:03+00:00">October 30, 2018</time>

        <div class="col-sm-4 col-xs-6 col-with-vspace">
            <div class="large-icon" id="link170660179">
                <span class="fa fa-file-video-o"></span>
                Video Clip
            </div>

            <!-- Modal -->
            <div class="modal fade" id="modal170660179" tabindex="-1" role="dialog" aria-labelledby="label170660179">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span></button>
                            <h4 class="modal-title" id="label170660179">Video Clip</h4>
                        </div>
                        <div class="modal-body">
                            <div class="embed-responsive embed-responsive-16by9">
                                <iframe class="embed-responsive-item" src="" webkitallowfullscreen mozallowfullscreen
                                allowfullscreen></iframe>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                jQuery('#link170660179').click(function () {
                    var src = 'http://video_link';
                    jQuery('#modal170660179').modal('show');
                    jQuery('#modal170660179 iframe').attr('src', src);
                });

                jQuery('#modal170660179 button').click(function () {
                    jQuery('#modal170660179 iframe').removeAttr('src');
                });
            </script>
        </div>

        <div class="col-sm-4 col-xs-6 col-with-vspace">
            <div class="large-icon" id="link264636963">
                <span class="fa fa-file-sound-o"></span>
                    Audio Clip
            </div>

            <!-- Modal -->
            <div class="modal fade" id="modal264636963" tabindex="-1" role="dialog" aria-labelledby="label264636963">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span></button>
                            <h4 class="modal-title" id="label264636963">Audio Clip</h4>
                        </div>
                        <div class="modal-body">
                            <div class="embed-responsive embed-responsive-16by9">
                                <iframe class="embed-responsive-item" src="" webkitallowfullscreen mozallowfullscreen
                                                                             allowfullscreen></iframe>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                jQuery('#link264636963').click(function () {
                    var src = 'http://audio_link';
                    jQuery('#modal264636963').modal('show');
                    jQuery('#modal264636963 iframe').attr('src', src);
                });

                jQuery('#modal264636963 button').click(function () {
                    jQuery('#modal264636963 iframe').removeAttr('src');
                });
            </script>
        </div>

        <div class="col-sm-4 col-xs-6 col-with-vspace">
            <p><a href="http://document.pdf" target="_blank" class="large-icon">
            <span class="fa fa-file-pdf-o"></span>Original Case Incident Report</a></p>
        </div>
    </div>
    '''

    @patch('data_importer.copa_crawler.portal_crawler.ComplaintCrawler.get_html_content')
    def test_parse(self, get_html_content):
        single_subject_content = '''
        <p>Subjects: Barry Hayes</p>
        '''

        get_html_content.return_value = self.HTML_CONTENT % single_subject_content
        records = {
            'attachments': [
                {'type': 'audio', 'link': 'http://audio_link', 'title': 'Audio Clip'},
                {'type': 'video', 'link': 'http://video_link', 'title': 'Video Clip'},
                {'type': 'document', 'link': 'http://document.pdf', 'title': 'Original Case Incident Report'}
            ],
            'date': '04-30-2013',
            'district': '04',
            'log_number': '1061883',
            'time': '04-30-2013 9:30 pm',
            'type': 'Firearm Discharge',
            'subjects': ['Barry Hayes'],
            'last_updated': '2018-10-30T15:00:03+00:00'
        }
        expect(ComplaintCrawler(url=self.URL).crawl()).to.be.eq(records)

    @patch('data_importer.copa_crawler.portal_crawler.ComplaintCrawler.get_html_content')
    def test_parse_with_multiple_subjects(self, get_html_content):
        multiple_subject_content = '''
        <p>Subjects:</p>
        <ul>
            <li>Barry Hayes</li>
            <li>Deandre Atwood</li>
            <li>Donald Harris</li>
        </ul>
        '''
        get_html_content.return_value = self.HTML_CONTENT % multiple_subject_content
        subjects = ['Barry Hayes', 'Deandre Atwood', 'Donald Harris']
        expect(ComplaintCrawler(url=self.URL).crawl()['subjects']).to.be.eq(subjects)

    # Mirrors current chicagocopa.org case pages: wide desktop row (7 columns), no incident type column.
    HTML_CONTENT_SEVEN_COLUMN = '''
    <div class="entry-content">
        <div class="table-responsive hidden-sm hidden-xs">
            <table class="table table-striped">
                <thead>
                <tr>
                    <th scope="col">Log#</th>
                    <th scope="col">Incident Date &amp; Time</th>
                    <th scope="col">District of Occurrence</th>
                    <th scope="col">COPA Notification Date</th>
                    <th scope="col">Transparency Release Date</th>
                    <th scope="col">Closed Date</th>
                    <th scope="col">FSR/Memo Posted Date</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <th scope="row">2026-0000682</th>
                    <td>02-05-2026 11:34 am</td>
                    <td>04</td>
                    <td>02-05-2026</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                </tr>
                </tbody>
            </table>
        </div>
        <div class="table-responsive hidden-xs hidden-md stack-table">
            <table>
            </table>
        </div>

        %s
        <time class="entry-date published" datetime="2018-10-30T15:00:03+00:00">October 30, 2018</time>

        <div class="col-sm-4 col-xs-6 col-with-vspace">
            <div class="large-icon" id="link170660179">
                <span class="fa fa-file-video-o"></span>
                Video Clip
            </div>
            <div class="modal fade" id="modal170660179" tabindex="-1" role="dialog" aria-labelledby="label170660179">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h4 class="modal-title" id="label170660179">Video Clip</h4>
                        </div>
                        <div class="modal-body">
                            <div class="embed-responsive embed-responsive-16by9">
                                <iframe class="embed-responsive-item" src=""></iframe>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script>
                jQuery('#link170660179').click(function () {
                    var src = 'http://video_link';
                    jQuery('#modal170660179').modal('show');
                    jQuery('#modal170660179 iframe').attr('src', src);
                });
            </script>
        </div>

        <div class="col-sm-4 col-xs-6 col-with-vspace">
            <div class="large-icon" id="link264636963">
                <span class="fa fa-file-sound-o"></span>
                    Audio Clip
            </div>
            <div class="modal fade" id="modal264636963" tabindex="-1" role="dialog" aria-labelledby="label264636963">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h4 class="modal-title" id="label264636963">Audio Clip</h4>
                        </div>
                        <div class="modal-body">
                            <div class="embed-responsive embed-responsive-16by9">
                                <iframe class="embed-responsive-item" src=""></iframe>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script>
                jQuery('#link264636963').click(function () {
                    var src = 'http://audio_link';
                    jQuery('#modal264636963').modal('show');
                    jQuery('#modal264636963 iframe').attr('src', src);
                });
            </script>
        </div>

        <div class="col-sm-4 col-xs-6 col-with-vspace">
            <p><a href="http://document.pdf" target="_blank" class="large-icon">
            <span class="fa fa-file-pdf-o"></span>Original Case Incident Report</a></p>
        </div>
    </div>
    '''

    @patch('data_importer.copa_crawler.portal_crawler.ComplaintCrawler.get_html_content')
    def test_parse_seven_column_case_portal_layout(self, get_html_content):
        get_html_content.return_value = self.HTML_CONTENT_SEVEN_COLUMN % '''
        <p>Subjects: Barry Hayes</p>
        '''
        records = {
            'attachments': [
                {'type': 'audio', 'link': 'http://audio_link', 'title': 'Audio Clip'},
                {'type': 'video', 'link': 'http://video_link', 'title': 'Video Clip'},
                {'type': 'document', 'link': 'http://document.pdf', 'title': 'Original Case Incident Report'}
            ],
            'date': '02-05-2026',
            'district': '04',
            'log_number': '2026-0000682',
            'time': '02-05-2026 11:34 am',
            'type': '',
            'subjects': ['Barry Hayes'],
            'last_updated': '2018-10-30T15:00:03+00:00'
        }
        expect(ComplaintCrawler(url=self.URL).crawl()).to.be.eq(records)


class VimeoSimpleAPITestCase(SimpleTestCase):
    @responses.activate
    def test_parse(self):
        content = [{
            'id': 307768537,
            'title': 'Log# 1082195 3rd Party Clip',
            'description': 'Log# 1082195 3rd Party Clip',
            'url': 'https://vimeo.com/307768537',
            'upload_date': '2018-12-21 15:47:48',
            'thumbnail_small': 'https://i.vimeocdn.com/video/747800241_100x75.webp',
            'thumbnail_medium': 'https://i.vimeocdn.com/video/747800241_200x150.webp',
            'thumbnail_large': 'https://i.vimeocdn.com/video/747800241_640.webp',
            'user_id': 51379210, 'user_name': 'COPA Chicago', 'user_url': 'https://vimeo.com/user51379210',
            'user_portrait_small': 'https://i.vimeocdn.com/portrait/21078020_30x30.webp',
            'user_portrait_medium': 'https://i.vimeocdn.com/portrait/21078020_75x75.webp',
            'user_portrait_large': 'https://i.vimeocdn.com/portrait/21078020_100x100.webp',
            'user_portrait_huge': 'https://i.vimeocdn.com/portrait/21078020_300x300.webp',
            'stats_number_of_likes': 0,
            'stats_number_of_plays': 16,
            'stats_number_of_comments': 0,
            'duration': 604,
            'width': 1280,
            'height': 720,
            'tags': '',
            'embed_privacy': 'anywhere'
        }]
        responses.add(
            responses.GET,
            'http://vimeo.com/api/v2/video/307768537.json',
            json=content,
            status=200
        )

        expect(VimeoSimpleAPI(video_id=307768537).crawl()).to.be.eq(content[0])

    @responses.activate
    def test_parse_no_content(self):
        responses.add(
            responses.GET,
            'http://vimeo.com/api/v2/video/307768537.json',
            status=404
        )
        expect(VimeoSimpleAPI(video_id=307768537).crawl()).to.be.eq(None)
