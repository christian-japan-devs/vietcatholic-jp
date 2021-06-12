import React from 'react';
//@Material-ui/core
import { makeStyles, Theme } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Grid from '@material-ui/core/Grid';
import Container from '@material-ui/core/Container';
//Components
import Layout from '../Layout';
import { MonthlyTopic, Props as TopicProps } from '../../components/TopicTheme/MonthlyTopic';
import Sidebar from '../Sections/Sidebar';
import MainSection from '../Sections/MainSection';
//Utils
import { apiDomain, monthlyTopicEnd, newfeedsURL } from '../../utils/apiEndpoint';
import { NewFeed } from '../../components/NewFeed';

const useStyles = makeStyles((theme: Theme) => ({
    mainGrid: {
        marginTop: theme.spacing(3),
    },
}));

const HomePage: React.FC = () => {
    var initTopic: TopicProps = {
        topic: {
            id: 1,
            image: '',
            imageText: '',
            title: '',
            description: { __html: '' },
            linkText: '/chu-de-thang/chi-tiet/',
            month: '',
        }
    }
    var initNewFeed: NewFeed[] = [];
    const [monthlyTopic, setMonthlyTopicTypes] = React.useState(initTopic);
    const [newFeeds, setNewFeeds] = React.useState(initNewFeed);
    const classes = useStyles();

    React.useEffect(() => {
        fetch(newfeedsURL, {
            method: 'get',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then((res) => {
            if (res.ok) {
                return res.json();
            }
            throw res;
        }).then((res) => {
            for (var index in res) {
                var data = res[index];
                var newFeed = {
                    id: data.id,
                    title: data.nf_title,
                    date: data.nf_date_created,
                    image: apiDomain + data.nf_image,
                    imageText: data.nf_title,
                    description: {
                        __html: data.nf_brief_content
                    },
                    detailUrl: '/bai-viet/chi-tiet/' + data.id,
                    type: data.nf_type,
                }
                setNewFeeds(newFeeds => [...newFeeds, newFeed]);
            }
        })

        fetch(monthlyTopicEnd, {
            method: 'get',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then((res) => {
            if (res.ok) {
                return res.json();
            }
            throw res;
        }).then((res) => {
            var data = res[0];
            if (data) {
                var topic = {
                    id: data.id,
                    image: apiDomain + data.mt_image_main,
                    imageText: data.mt_image_main_text,
                    title: data.mt_title,
                    description: {
                        __html: data.mt_brief_content
                    },
                    linkText: '/monthly-topic/detail/' + data.mt_month,
                    month: data.mt_month,
                }
                setMonthlyTopicTypes({
                    ...monthlyTopic,
                    topic: topic
                })
            }
        })
    }, []);
    return (
        <Layout>
            <CssBaseline />
            <Container maxWidth='lg'>
                <MonthlyTopic topic={monthlyTopic.topic} />
                <Grid container spacing={5} className={classes.mainGrid}>
                    <Grid item xs={12} md={8}>

                        <MainSection title='Thư mục vụ' posts={newFeeds} />
                        <MainSection title='Tin tức' posts={newFeeds} />
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <Sidebar title='Giới trẻ' posts={newFeeds} />
                        <Sidebar title='Văn hoá Nhật' posts={newFeeds} />
                    </Grid>
                </Grid>
            </Container>
        </Layout>
    );
};

export default HomePage;