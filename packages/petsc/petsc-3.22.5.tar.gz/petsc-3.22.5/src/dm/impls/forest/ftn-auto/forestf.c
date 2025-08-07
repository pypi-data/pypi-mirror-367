#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* forest.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmforest.h"
#include "petscdm.h"
#include "petscdmlabel.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmisforest_ DMISFOREST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmisforest_ dmisforest
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforesttemplate_ DMFORESTTEMPLATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforesttemplate_ dmforesttemplate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsettopology_ DMFORESTSETTOPOLOGY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsettopology_ dmforestsettopology
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgettopology_ DMFORESTGETTOPOLOGY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgettopology_ dmforestgettopology
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetbasedm_ DMFORESTSETBASEDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetbasedm_ dmforestsetbasedm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetbasedm_ DMFORESTGETBASEDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetbasedm_ dmforestgetbasedm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetadaptivityforest_ DMFORESTSETADAPTIVITYFOREST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetadaptivityforest_ dmforestsetadaptivityforest
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetadaptivityforest_ DMFORESTGETADAPTIVITYFOREST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetadaptivityforest_ dmforestgetadaptivityforest
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetadaptivitypurpose_ DMFORESTSETADAPTIVITYPURPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetadaptivitypurpose_ dmforestsetadaptivitypurpose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetadaptivitypurpose_ DMFORESTGETADAPTIVITYPURPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetadaptivitypurpose_ dmforestgetadaptivitypurpose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetadjacencydimension_ DMFORESTSETADJACENCYDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetadjacencydimension_ dmforestsetadjacencydimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetadjacencycodimension_ DMFORESTSETADJACENCYCODIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetadjacencycodimension_ dmforestsetadjacencycodimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetadjacencydimension_ DMFORESTGETADJACENCYDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetadjacencydimension_ dmforestgetadjacencydimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetadjacencycodimension_ DMFORESTGETADJACENCYCODIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetadjacencycodimension_ dmforestgetadjacencycodimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetpartitionoverlap_ DMFORESTSETPARTITIONOVERLAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetpartitionoverlap_ dmforestsetpartitionoverlap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetpartitionoverlap_ DMFORESTGETPARTITIONOVERLAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetpartitionoverlap_ dmforestgetpartitionoverlap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetminimumrefinement_ DMFORESTSETMINIMUMREFINEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetminimumrefinement_ dmforestsetminimumrefinement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetminimumrefinement_ DMFORESTGETMINIMUMREFINEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetminimumrefinement_ dmforestgetminimumrefinement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetinitialrefinement_ DMFORESTSETINITIALREFINEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetinitialrefinement_ dmforestsetinitialrefinement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetinitialrefinement_ DMFORESTGETINITIALREFINEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetinitialrefinement_ dmforestgetinitialrefinement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetmaximumrefinement_ DMFORESTSETMAXIMUMREFINEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetmaximumrefinement_ dmforestsetmaximumrefinement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetmaximumrefinement_ DMFORESTGETMAXIMUMREFINEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetmaximumrefinement_ dmforestgetmaximumrefinement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetadaptivitystrategy_ DMFORESTSETADAPTIVITYSTRATEGY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetadaptivitystrategy_ dmforestsetadaptivitystrategy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetadaptivitystrategy_ DMFORESTGETADAPTIVITYSTRATEGY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetadaptivitystrategy_ dmforestgetadaptivitystrategy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetadaptivitysuccess_ DMFORESTGETADAPTIVITYSUCCESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetadaptivitysuccess_ dmforestgetadaptivitysuccess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetcomputeadaptivitysf_ DMFORESTSETCOMPUTEADAPTIVITYSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetcomputeadaptivitysf_ dmforestsetcomputeadaptivitysf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetcomputeadaptivitysf_ DMFORESTGETCOMPUTEADAPTIVITYSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetcomputeadaptivitysf_ dmforestgetcomputeadaptivitysf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetadaptivitysf_ DMFORESTGETADAPTIVITYSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetadaptivitysf_ dmforestgetadaptivitysf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetgradefactor_ DMFORESTSETGRADEFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetgradefactor_ dmforestsetgradefactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetgradefactor_ DMFORESTGETGRADEFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetgradefactor_ dmforestgetgradefactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetcellweightfactor_ DMFORESTSETCELLWEIGHTFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetcellweightfactor_ dmforestsetcellweightfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetcellweightfactor_ DMFORESTGETCELLWEIGHTFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetcellweightfactor_ dmforestgetcellweightfactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetcellchart_ DMFORESTGETCELLCHART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetcellchart_ dmforestgetcellchart
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetcellsf_ DMFORESTGETCELLSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetcellsf_ dmforestgetcellsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetadaptivitylabel_ DMFORESTSETADAPTIVITYLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetadaptivitylabel_ dmforestsetadaptivitylabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetadaptivitylabel_ DMFORESTGETADAPTIVITYLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetadaptivitylabel_ dmforestgetadaptivitylabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetcellweights_ DMFORESTSETCELLWEIGHTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetcellweights_ dmforestsetcellweights
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetcellweights_ DMFORESTGETCELLWEIGHTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetcellweights_ dmforestgetcellweights
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestsetweightcapacity_ DMFORESTSETWEIGHTCAPACITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestsetweightcapacity_ dmforestsetweightcapacity
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmforestgetweightcapacity_ DMFORESTGETWEIGHTCAPACITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmforestgetweightcapacity_ dmforestgetweightcapacity
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmisforest_(DM dm,PetscBool *isForest, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMIsForest(
	(DM)PetscToPointer((dm) ),isForest);
}
PETSC_EXTERN void  dmforesttemplate_(DM dm,MPI_Fint * comm,DM *tdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool tdm_null = !*(void**) tdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tdm);
*ierr = DMForestTemplate(
	(DM)PetscToPointer((dm) ),
	MPI_Comm_f2c(*(comm)),tdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tdm_null && !*(void**) tdm) * (void **) tdm = (void *)-2;
}
PETSC_EXTERN void  dmforestsettopology_(DM dm,char *topology, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for topology */
  FIXCHAR(topology,cl0,_cltmp0);
*ierr = DMForestSetTopology(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(topology,_cltmp0);
}
PETSC_EXTERN void  dmforestgettopology_(DM dm,char *topology, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestGetTopology(
	(DM)PetscToPointer((dm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for topology */
*ierr = PetscStrncpy(topology, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, topology, cl0);
}
PETSC_EXTERN void  dmforestsetbasedm_(DM dm,DM base, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(base);
*ierr = DMForestSetBaseDM(
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((base) ));
}
PETSC_EXTERN void  dmforestgetbasedm_(DM dm,DM *base, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool base_null = !*(void**) base ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(base);
*ierr = DMForestGetBaseDM(
	(DM)PetscToPointer((dm) ),base);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! base_null && !*(void**) base) * (void **) base = (void *)-2;
}
PETSC_EXTERN void  dmforestsetadaptivityforest_(DM dm,DM adapt, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(adapt);
*ierr = DMForestSetAdaptivityForest(
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((adapt) ));
}
PETSC_EXTERN void  dmforestgetadaptivityforest_(DM dm,DM *adapt, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool adapt_null = !*(void**) adapt ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(adapt);
*ierr = DMForestGetAdaptivityForest(
	(DM)PetscToPointer((dm) ),adapt);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! adapt_null && !*(void**) adapt) * (void **) adapt = (void *)-2;
}
PETSC_EXTERN void  dmforestsetadaptivitypurpose_(DM dm,DMAdaptFlag *purpose, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetAdaptivityPurpose(
	(DM)PetscToPointer((dm) ),*purpose);
}
PETSC_EXTERN void  dmforestgetadaptivitypurpose_(DM dm,DMAdaptFlag *purpose, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestGetAdaptivityPurpose(
	(DM)PetscToPointer((dm) ),purpose);
}
PETSC_EXTERN void  dmforestsetadjacencydimension_(DM dm,PetscInt *adjDim, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetAdjacencyDimension(
	(DM)PetscToPointer((dm) ),*adjDim);
}
PETSC_EXTERN void  dmforestsetadjacencycodimension_(DM dm,PetscInt *adjCodim, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetAdjacencyCodimension(
	(DM)PetscToPointer((dm) ),*adjCodim);
}
PETSC_EXTERN void  dmforestgetadjacencydimension_(DM dm,PetscInt *adjDim, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(adjDim);
*ierr = DMForestGetAdjacencyDimension(
	(DM)PetscToPointer((dm) ),adjDim);
}
PETSC_EXTERN void  dmforestgetadjacencycodimension_(DM dm,PetscInt *adjCodim, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(adjCodim);
*ierr = DMForestGetAdjacencyCodimension(
	(DM)PetscToPointer((dm) ),adjCodim);
}
PETSC_EXTERN void  dmforestsetpartitionoverlap_(DM dm,PetscInt *overlap, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetPartitionOverlap(
	(DM)PetscToPointer((dm) ),*overlap);
}
PETSC_EXTERN void  dmforestgetpartitionoverlap_(DM dm,PetscInt *overlap, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(overlap);
*ierr = DMForestGetPartitionOverlap(
	(DM)PetscToPointer((dm) ),overlap);
}
PETSC_EXTERN void  dmforestsetminimumrefinement_(DM dm,PetscInt *minRefinement, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetMinimumRefinement(
	(DM)PetscToPointer((dm) ),*minRefinement);
}
PETSC_EXTERN void  dmforestgetminimumrefinement_(DM dm,PetscInt *minRefinement, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(minRefinement);
*ierr = DMForestGetMinimumRefinement(
	(DM)PetscToPointer((dm) ),minRefinement);
}
PETSC_EXTERN void  dmforestsetinitialrefinement_(DM dm,PetscInt *initRefinement, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetInitialRefinement(
	(DM)PetscToPointer((dm) ),*initRefinement);
}
PETSC_EXTERN void  dmforestgetinitialrefinement_(DM dm,PetscInt *initRefinement, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(initRefinement);
*ierr = DMForestGetInitialRefinement(
	(DM)PetscToPointer((dm) ),initRefinement);
}
PETSC_EXTERN void  dmforestsetmaximumrefinement_(DM dm,PetscInt *maxRefinement, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetMaximumRefinement(
	(DM)PetscToPointer((dm) ),*maxRefinement);
}
PETSC_EXTERN void  dmforestgetmaximumrefinement_(DM dm,PetscInt *maxRefinement, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(maxRefinement);
*ierr = DMForestGetMaximumRefinement(
	(DM)PetscToPointer((dm) ),maxRefinement);
}
PETSC_EXTERN void  dmforestsetadaptivitystrategy_(DM dm,char *adaptStrategy, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for adaptStrategy */
  FIXCHAR(adaptStrategy,cl0,_cltmp0);
*ierr = DMForestSetAdaptivityStrategy(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(adaptStrategy,_cltmp0);
}
PETSC_EXTERN void  dmforestgetadaptivitystrategy_(DM dm,char *adaptStrategy, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestGetAdaptivityStrategy(
	(DM)PetscToPointer((dm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for adaptStrategy */
*ierr = PetscStrncpy(adaptStrategy, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, adaptStrategy, cl0);
}
PETSC_EXTERN void  dmforestgetadaptivitysuccess_(DM dm,PetscBool *success, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestGetAdaptivitySuccess(
	(DM)PetscToPointer((dm) ),success);
}
PETSC_EXTERN void  dmforestsetcomputeadaptivitysf_(DM dm,PetscBool *computeSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetComputeAdaptivitySF(
	(DM)PetscToPointer((dm) ),*computeSF);
}
PETSC_EXTERN void  dmforestgetcomputeadaptivitysf_(DM dm,PetscBool *computeSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestGetComputeAdaptivitySF(
	(DM)PetscToPointer((dm) ),computeSF);
}
PETSC_EXTERN void  dmforestgetadaptivitysf_(DM dm,PetscSF *preCoarseToFine,PetscSF *coarseToPreFine, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool preCoarseToFine_null = !*(void**) preCoarseToFine ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(preCoarseToFine);
PetscBool coarseToPreFine_null = !*(void**) coarseToPreFine ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(coarseToPreFine);
*ierr = DMForestGetAdaptivitySF(
	(DM)PetscToPointer((dm) ),preCoarseToFine,coarseToPreFine);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! preCoarseToFine_null && !*(void**) preCoarseToFine) * (void **) preCoarseToFine = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! coarseToPreFine_null && !*(void**) coarseToPreFine) * (void **) coarseToPreFine = (void *)-2;
}
PETSC_EXTERN void  dmforestsetgradefactor_(DM dm,PetscInt *grade, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetGradeFactor(
	(DM)PetscToPointer((dm) ),*grade);
}
PETSC_EXTERN void  dmforestgetgradefactor_(DM dm,PetscInt *grade, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(grade);
*ierr = DMForestGetGradeFactor(
	(DM)PetscToPointer((dm) ),grade);
}
PETSC_EXTERN void  dmforestsetcellweightfactor_(DM dm,PetscReal *weightsFactor, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetCellWeightFactor(
	(DM)PetscToPointer((dm) ),*weightsFactor);
}
PETSC_EXTERN void  dmforestgetcellweightfactor_(DM dm,PetscReal *weightsFactor, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(weightsFactor);
*ierr = DMForestGetCellWeightFactor(
	(DM)PetscToPointer((dm) ),weightsFactor);
}
PETSC_EXTERN void  dmforestgetcellchart_(DM dm,PetscInt *cStart,PetscInt *cEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(cStart);
CHKFORTRANNULLINTEGER(cEnd);
*ierr = DMForestGetCellChart(
	(DM)PetscToPointer((dm) ),cStart,cEnd);
}
PETSC_EXTERN void  dmforestgetcellsf_(DM dm,PetscSF *cellSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool cellSF_null = !*(void**) cellSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cellSF);
*ierr = DMForestGetCellSF(
	(DM)PetscToPointer((dm) ),cellSF);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cellSF_null && !*(void**) cellSF) * (void **) cellSF = (void *)-2;
}
PETSC_EXTERN void  dmforestsetadaptivitylabel_(DM dm,DMLabel adaptLabel, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(adaptLabel);
*ierr = DMForestSetAdaptivityLabel(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((adaptLabel) ));
}
PETSC_EXTERN void  dmforestgetadaptivitylabel_(DM dm,DMLabel *adaptLabel, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool adaptLabel_null = !*(void**) adaptLabel ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(adaptLabel);
*ierr = DMForestGetAdaptivityLabel(
	(DM)PetscToPointer((dm) ),adaptLabel);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! adaptLabel_null && !*(void**) adaptLabel) * (void **) adaptLabel = (void *)-2;
}
PETSC_EXTERN void  dmforestsetcellweights_(DM dm,PetscReal weights[],PetscCopyMode *copyMode, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(weights);
*ierr = DMForestSetCellWeights(
	(DM)PetscToPointer((dm) ),weights,*copyMode);
}
PETSC_EXTERN void  dmforestgetcellweights_(DM dm,PetscReal **weights, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(weights);
*ierr = DMForestGetCellWeights(
	(DM)PetscToPointer((dm) ),weights);
}
PETSC_EXTERN void  dmforestsetweightcapacity_(DM dm,PetscReal *capacity, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMForestSetWeightCapacity(
	(DM)PetscToPointer((dm) ),*capacity);
}
PETSC_EXTERN void  dmforestgetweightcapacity_(DM dm,PetscReal *capacity, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(capacity);
*ierr = DMForestGetWeightCapacity(
	(DM)PetscToPointer((dm) ),capacity);
}
#if defined(__cplusplus)
}
#endif
