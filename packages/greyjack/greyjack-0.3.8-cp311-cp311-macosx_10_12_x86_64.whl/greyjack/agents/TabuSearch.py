
from greyjack.agents.base.Agent import Agent
from greyjack.agents.metaheuristic_bases.TabuSearchBase import TabuSearchBase
from greyjack.score_calculation.score_requesters.OOPScoreRequester import OOPScoreRequester
from greyjack.score_calculation.score_requesters.PureMathScoreRequester import PureMathScoreRequester
from greyjack.cotwin.CotwinBase import CotwinBase
from greyjack.pure_math.MathModel import MathModel

class TabuSearch(Agent):
    def __init__(
        self,
        neighbours_count,
        tabu_entity_rate,
        mutation_rate_multiplier=None,
        move_probas=None,
        migration_frequency=999_999_999,
        compare_to_global_frequency=1, # Tabu is usually not too fast-stepping due to high neighbours_count
        termination_strategy=None,
    ):
        
        super().__init__(1.0, migration_frequency, termination_strategy, compare_to_global_frequency)

        self.population_size = 1
        self.neighbours_count = neighbours_count
        self.tabu_entity_rate = tabu_entity_rate
        self.mutation_rate_multiplier = mutation_rate_multiplier
        self.move_probas = move_probas

        # If true - stucks more often in local minimums, but converges much faster
        # may be useful in multiple stages solving
        self.is_win_from_comparing_with_global = True

    def _build_metaheuristic_base(self):
        if hasattr(self.cotwin, "planning_entities"):
            self.score_requester = OOPScoreRequester(self.cotwin)
            score_variant = self.cotwin.score_calculator.score_variant
        elif isinstance(self.cotwin, MathModel):
            self.score_requester = PureMathScoreRequester(self.cotwin)
            score_variant = self.cotwin.score_variant
            self.cotwin.score_calculator.is_incremental = False
        else:
            raise Exception("Cotwin must be either subclass of CotwinBase, or an instance of MathModel")

        semantic_groups_dict = self.score_requester.variables_manager.semantic_groups_map.copy()
        discrete_ids = self.score_requester.variables_manager.discrete_ids

        self.metaheuristic_base = TabuSearchBase.new(
            score_variant,
            self.score_requester.variables_manager,
            self.neighbours_count,
            self.tabu_entity_rate,
            semantic_groups_dict,
            self.mutation_rate_multiplier,
            self.move_probas.copy() if self.move_probas else None,
            discrete_ids,
        )

        self.metaheuristic_name = self.metaheuristic_base.metaheuristic_name
        self.metaheuristic_kind = self.metaheuristic_base.metaheuristic_kind

        return self