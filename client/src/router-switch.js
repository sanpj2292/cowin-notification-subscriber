import { Switch, Route } from 'react-router-dom';
import { Typography } from '@material-ui/core';
import EmailSubscribe from './components/email-subscribe';
import Subscriptions from './components/subscriptions';

export default function RouterSwitch() {
    return (
    <Switch>
        <Route path="/" exact component={EmailSubscribe}>
        </Route>
        <Route path="/subscriptions" exact component={Subscriptions}>
        </Route>
    </Switch>
    )
}