import { Switch, Route } from 'react-router-dom';
import { Typography } from '@material-ui/core';
import EmailSubscribe from './components/email-subscribe';
import Subscriptions from './components/subscriptions';
import SubscriptionAvailability from './components/subscription-availability';

export default function RouterSwitch() {
    return (
    <Switch>
        <Route path="/" exact component={EmailSubscribe}>
        </Route>
        <Route path="/subscriptions" exact component={Subscriptions}>
        </Route>
        <Route path="/stream/subscriptions" exact component={SubscriptionAvailability}>
        </Route>
    </Switch>
    )
}